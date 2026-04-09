#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import asdict, dataclass
from statistics import mean
from time import perf_counter
from typing import Any

from ollama import Client


DEFAULT_MODELS = (
    "gemma4:e4b",
    "translategemma:4b",
    "deepseek-r1:7b",
    "deepseek-r1:1.5b",
    "llama3.2:3b",
)

DEFAULT_PROMPT = """
Role: Act as an elite, award-winning novelist and screenwriter specializing in [INSERT GENRE, e.g., Hard Sci-Fi / Gothic Horror / Noir Mystery]. Your writing style is characterized by visceral sensory details, psychological depth, and high-stakes subtext.

Objective: Write a sophisticated standalone story based on this premise:
I want a story about a young child that played games and got hacked. This pushed him to become  ahacker himself.

Structural & Stylistic Requirements:
- Sensory Grounding: Use the "Show, Don't Tell" principle. Describe the specific quality of light, the grit of the textures, the ambient hum of the environment, and the scent of the air. Avoid generic adjectives; use precise nouns and active verbs.
- Character Interiority: We must live inside the protagonist's mind. Focus on their cognitive biases, their physiological reactions to stress (e.g., the copper taste of fear, the weight in the lungs), and the things they refuse to admit to themselves.
- Dialogue with Subtext: Characters should rarely say exactly what they mean. Use dialogue to negotiate power, hide secrets, or deflect. Include "beats" (physical actions during speech) to show their internal state.

Narrative Pacing:
- The Hook: Begin in media res at a point of high tension or immediate curiosity.
- The Complication: Introduce a specific technical, emotional, or physical obstacle that forces the protagonist to change their plan.
- The Climax: A moment of irreversible choice where the protagonist’s core values are tested.
- The Resolution: A "haunting" ending. Avoid neat bows; leave the reader with a lingering image or a philosophical question.

Technical Constraints:
- Tone: [INSERT TONE, e.g., Melancholic and Cold / High-Octane and Kinetic / Dreamlike and Ethereal].
- Vocabulary: Use sophisticated, domain-specific terminology relevant to the setting.
- Prohibitions: Strictly avoid AI clichés (e.g., "In a world where...", "Little did he know...", "A testament to..."). No "happily ever after" tropes.

Operational Instruction: Before writing the story, provide a one-sentence "Logline" and a one-sentence "Twist/Revelation" that you intend to use. Once those are established, proceed immediately to the full narrative.
"""


@dataclass
class BenchmarkRun:
    model: str
    run_index: int
    output_tokens: int
    output_eval_s: float
    output_tps: float
    prompt_tokens: int
    prompt_eval_s: float
    prompt_tps: float
    total_s: float
    load_s: float
    wall_s: float
    response_chars: int


@dataclass
class BenchmarkError:
    model: str
    error: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Benchmark local Ollama models by output tokens/second."
    )
    parser.add_argument(
        "--models",
        nargs="+",
        default=list(DEFAULT_MODELS),
        help="Models to benchmark. Defaults to the five models requested.",
    )
    parser.add_argument(
        "--host",
        default=resolve_host(),
        help="Ollama host URL. Defaults to OLLAMA_HOST/OLLAMA_URL or http://<OLLAMA_REMOTE_IP>:11434.",
    )
    parser.add_argument(
        "--prompt",
        default=DEFAULT_PROMPT,
        help="Prompt used for the benchmark.",
    )
    parser.add_argument(
        "--repeat",
        type=int,
        default=1,
        help="Measured runs per model.",
    )
    parser.add_argument(
        "--warmup",
        type=int,
        default=0,
        help="Warmup runs per model before measuring.",
    )
    parser.add_argument(
        "--num-predict",
        type=int,
        default=256,
        help="Maximum generated tokens requested from Ollama.",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.0,
        help="Sampling temperature.",
    )
    parser.add_argument(
        "--keep-alive",
        default="10m",
        help="Ollama keep_alive value.",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=600.0,
        help="Client timeout in seconds.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit JSON instead of a table.",
    )
    return parser.parse_args()


def resolve_host() -> str:
    if os.getenv("OLLAMA_HOST"):
        return os.environ["OLLAMA_HOST"]
    if os.getenv("OLLAMA_URL"):
        return os.environ["OLLAMA_URL"]
    remote_ip = os.getenv("OLLAMA_REMOTE_IP", "172.24.32.1")
    return f"http://{remote_ip}:11434"


def ns_to_s(value: Any) -> float:
    if not value:
        return 0.0
    return float(value) / 1_000_000_000.0


def safe_tps(tokens: Any, seconds: float) -> float:
    token_count = int(tokens or 0)
    if token_count <= 0 or seconds <= 0:
        return 0.0
    return token_count / seconds


def response_to_dict(response: Any) -> dict[str, Any]:
    if hasattr(response, "model_dump"):
        return response.model_dump()
    return dict(response)


def extract_available_models(response: Any) -> set[str]:
    data = response_to_dict(response)
    names: set[str] = set()
    for item in data.get("models", []):
        if isinstance(item, dict) and item.get("model"):
            names.add(str(item["model"]))
            continue
        name = getattr(item, "model", None)
        if name:
            names.add(str(name))
    return names


def measure_once(
    client: Client,
    model: str,
    prompt: str,
    run_index: int,
    num_predict: int,
    temperature: float,
    keep_alive: str,
) -> BenchmarkRun:
    started = perf_counter()
    stream = client.generate(
        model=model,
        prompt=prompt,
        stream=True,
        think=False,
        keep_alive=keep_alive,
        options={
            "temperature": temperature,
            "num_predict": num_predict,
            "seed": 1337,
        },
    )
    data: dict[str, Any] = {}
    content_parts: list[str] = []
    for chunk in stream:
        data = response_to_dict(chunk)
        content = data.get("response") or ""
        if content:
            content_parts.append(content)
    wall_s = perf_counter() - started

    output_eval_s = ns_to_s(data.get("eval_duration"))
    prompt_eval_s = ns_to_s(data.get("prompt_eval_duration"))
    total_s = ns_to_s(data.get("total_duration"))
    load_s = ns_to_s(data.get("load_duration"))
    output_tokens = int(data.get("eval_count") or 0)
    prompt_tokens = int(data.get("prompt_eval_count") or 0)

    return BenchmarkRun(
        model=model,
        run_index=run_index,
        output_tokens=output_tokens,
        output_eval_s=output_eval_s,
        output_tps=safe_tps(output_tokens, output_eval_s),
        prompt_tokens=prompt_tokens,
        prompt_eval_s=prompt_eval_s,
        prompt_tps=safe_tps(prompt_tokens, prompt_eval_s),
        total_s=total_s,
        load_s=load_s,
        wall_s=wall_s,
        response_chars=len("".join(content_parts)),
    )


def format_float(value: float) -> str:
    return f"{value:.2f}"


def render_table(runs: list[BenchmarkRun], errors: list[BenchmarkError]) -> str:
    lines: list[str] = []
    headers = (
        ("model", "Model"),
        ("run_index", "Run"),
        ("output_tps", "Out tok/s"),
        ("output_tokens", "Out toks"),
        ("output_eval_s", "Eval s"),
        ("total_s", "Total s"),
        ("load_s", "Load s"),
        ("wall_s", "Wall s"),
    )
    rows: list[dict[str, str]] = []
    for run in runs:
        rows.append(
            {
                "model": run.model,
                "run_index": str(run.run_index),
                "output_tps": format_float(run.output_tps),
                "output_tokens": str(run.output_tokens),
                "output_eval_s": format_float(run.output_eval_s),
                "total_s": format_float(run.total_s),
                "load_s": format_float(run.load_s),
                "wall_s": format_float(run.wall_s),
            }
        )

    widths: dict[str, int] = {}
    for key, label in headers:
        widths[key] = max(len(label), *(len(row[key]) for row in rows)) if rows else len(label)

    header_line = "  ".join(label.ljust(widths[key]) for key, label in headers)
    separator = "  ".join("-" * widths[key] for key, _ in headers)
    lines.extend([header_line, separator])
    for row in rows:
        lines.append("  ".join(row[key].ljust(widths[key]) for key, _ in headers))

    if runs:
        lines.append("")
        lines.append("Average output tok/s by model:")
        for model in sorted({run.model for run in runs}):
            model_runs = [run for run in runs if run.model == model]
            avg = mean(run.output_tps for run in model_runs)
            best = max(run.output_tps for run in model_runs)
            lines.append(
                f"- {model}: avg={format_float(avg)} tok/s, best={format_float(best)} tok/s"
            )

    if errors:
        lines.append("")
        lines.append("Errors:")
        for error in errors:
            lines.append(f"- {error.model}: {error.error}")

    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    client = Client(host=args.host, timeout=args.timeout)
    available_models = extract_available_models(client.list())

    runs: list[BenchmarkRun] = []
    errors: list[BenchmarkError] = []

    for model in args.models:
        if available_models and model not in available_models:
            errors.append(BenchmarkError(model=model, error="model not found in ollama list"))
            continue

        for _ in range(max(args.warmup, 0)):
            try:
                warmup_stream = client.generate(
                    model=model,
                    prompt="Say benchmark once.",
                    stream=True,
                    think=False,
                    keep_alive=args.keep_alive,
                    options={
                        "temperature": 0,
                        "num_predict": 8,
                        "seed": 1337,
                    },
                )
                for _chunk in warmup_stream:
                    pass
            except Exception as exc:
                errors.append(BenchmarkError(model=model, error=f"warmup failed: {exc}"))
                break
        else:
            for run_index in range(1, max(args.repeat, 1) + 1):
                try:
                    runs.append(
                        measure_once(
                            client=client,
                            model=model,
                            prompt=args.prompt,
                            run_index=run_index,
                            num_predict=args.num_predict,
                            temperature=args.temperature,
                            keep_alive=args.keep_alive,
                        )
                    )
                except Exception as exc:
                    errors.append(BenchmarkError(model=model, error=str(exc)))
                    break

    if args.json:
        payload = {
            "host": args.host,
            "prompt": args.prompt,
            "repeat": args.repeat,
            "warmup": args.warmup,
            "num_predict": args.num_predict,
            "runs": [asdict(run) for run in runs],
            "errors": [asdict(error) for error in errors],
        }
        print(json.dumps(payload, indent=2))
    else:
        print(f"Ollama host: {args.host}")
        print(f"Prompt: {args.prompt}")
        print(f"Repeat: {args.repeat} | Warmup: {args.warmup} | num_predict: {args.num_predict}")
        print("")
        print(render_table(runs, errors))

    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
