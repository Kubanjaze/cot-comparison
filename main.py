import sys
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

import argparse, os, json, re, warnings
warnings.filterwarnings("ignore")
import pandas as pd
from dotenv import load_dotenv
import anthropic

load_dotenv()
os.environ.setdefault("ANTHROPIC_API_KEY", os.getenv("ANTHROPIC_API_KEY", ""))


def build_sar_context(df: pd.DataFrame) -> str:
    lines = []
    for _, row in df.iterrows():
        fam = row["compound_name"].split("_")[0]
        lines.append(f"{row['compound_name']}: pIC50={row['pic50']:.2f} [{fam}]")
    return "\n".join(lines)


QUESTION = "Which scaffold family should we prioritize for lead optimization, and why? Consider potency, consistency, and room for improvement."


def score_response(text: str, df: pd.DataFrame) -> dict:
    """Score response quality on 4 objective criteria."""
    text_lower = text.lower()
    # 1. Mentions specific pIC50 values (look for numbers like 7.25, 8.10)
    pic50_matches = re.findall(r'\d\.\d{1,2}', text)
    has_pic50 = len(pic50_matches) >= 2

    # 2. Compares multiple scaffold families
    families = ["benz", "naph", "ind", "quin", "pyr", "bzim"]
    mentioned = sum(1 for f in families if f in text_lower)
    compares_scaffolds = mentioned >= 3

    # 3. Gives clear recommendation (one family named)
    has_recommendation = any(f"{f} " in text_lower or f"{f})" in text_lower or f"{f}," in text_lower
                             for f in families)

    # 4. Cites evidence (mentions mean, range, or specific compound names)
    has_evidence = any(kw in text_lower for kw in ["mean", "average", "range", "highest", "lowest", "best"])

    return {
        "has_pic50_values": has_pic50,
        "compares_scaffolds": compares_scaffolds,
        "has_recommendation": has_recommendation,
        "has_evidence": has_evidence,
        "total_score": sum([has_pic50, compares_scaffolds, has_recommendation, has_evidence]),
    }


def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--input", required=True)
    parser.add_argument("--model", default="claude-haiku-4-5-20251001")
    parser.add_argument("--output-dir", default="output")
    args = parser.parse_args()
    os.makedirs(args.output_dir, exist_ok=True)

    df = pd.read_csv(args.input)
    context = build_sar_context(df)
    client = anthropic.Anthropic()

    print(f"\nPhase 72 — CoT vs Direct Answer")
    print(f"Model: {args.model}\n")

    prompts = {
        "direct": f"Here is SAR data for CETP inhibitor compounds:\n\n{context}\n\n{QUESTION}\n\nAnswer concisely.",
        "cot": f"Here is SAR data for CETP inhibitor compounds:\n\n{context}\n\n{QUESTION}\n\n"
               "Think step by step:\n"
               "Step 1: Calculate the mean pIC50 for each scaffold family.\n"
               "Step 2: Identify which family has the best and worst potency.\n"
               "Step 3: Consider the potency range (consistency) within each family.\n"
               "Step 4: Recommend the best family for lead optimization with evidence.",
    }

    results = {}
    total_input = 0
    total_output = 0

    for mode, prompt in prompts.items():
        response = client.messages.create(model=args.model, max_tokens=1024, messages=[{"role": "user", "content": prompt}])
        text = "".join(b.text for b in response.content if hasattr(b, "text"))
        total_input += response.usage.input_tokens
        total_output += response.usage.output_tokens

        scores = score_response(text, df)
        print(f"--- {mode.upper()} ---")
        print(f"Response ({len(text)} chars, {response.usage.output_tokens} tokens):")
        print(f"{text[:300]}...\n")
        print(f"Quality: {scores['total_score']}/4 | pic50={scores['has_pic50_values']} scaffolds={scores['compares_scaffolds']} rec={scores['has_recommendation']} evidence={scores['has_evidence']}\n")

        results[mode] = {
            "response": text, "response_length": len(text),
            "output_tokens": response.usage.output_tokens,
            "scores": scores,
        }

    cost = (total_input / 1e6 * 0.80) + (total_output / 1e6 * 4.0)
    report = (
        f"Phase 72 — CoT vs Direct Answer\n{'='*50}\n"
        f"Model: {args.model}\n\n"
        f"Direct: {results['direct']['scores']['total_score']}/4 quality | {results['direct']['output_tokens']} tokens\n"
        f"CoT:    {results['cot']['scores']['total_score']}/4 quality | {results['cot']['output_tokens']} tokens\n\n"
        f"Tokens: in={total_input} out={total_output}\nCost: ${cost:.4f}\n"
    )
    print(report)

    with open(os.path.join(args.output_dir, "cot_comparison.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    with open(os.path.join(args.output_dir, "cot_report.txt"), "w", encoding="utf-8") as f:
        f.write(report)
    print("Done.")


if __name__ == "__main__":
    main()
