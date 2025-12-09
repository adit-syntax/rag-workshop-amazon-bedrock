#!/usr/bin/env python3
"""
RAG Evaluation Script
Evaluates RAG system using RAGAS framework
"""

import json
import pandas as pd
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall,
    context_entity_recall,
    answer_similarity,
    answer_correctness
)
from datasets import Dataset

def load_evaluation_data(file_path="outputs/evaluation_data.json"):
    """Load evaluation dataset"""
    print(f"📂 Loading evaluation data from {file_path}")
    
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        print(f"❌ File not found: {file_path}")
        return None

def prepare_dataset(data):
    """Prepare dataset for RAGAS evaluation"""
    print("\n📋 Preparing dataset for evaluation...")
    
    dataset = Dataset.from_dict({
        'question': data.get('questions', []),
        'answer': data.get('answers', []),
        'contexts': data.get('contexts', []),
        'ground_truth': data.get('ground_truths', [])
    })
    
    print(f"✅ Dataset prepared with {len(dataset)} samples")
    return dataset

def run_evaluation(dataset):
    """Run RAGAS evaluation"""
    print("\n🔄 Running RAGAS evaluation...")
    print("This may take a few minutes...\n")
    
    metrics = [
        faithfulness,
        answer_relevancy,
        context_precision,
        context_recall,
        context_entity_recall,
        answer_similarity,
        answer_correctness
    ]
    
    try:
        results = evaluate(
            dataset=dataset,
            metrics=metrics,
            raise_exceptions=False
        )
        return results
    except Exception as e:
        print(f"❌ Error during evaluation: {e}")
        return None

def save_results(results, output_file="outputs/evaluation_results.json"):
    """Save evaluation results"""
    print(f"\n💾 Saving results to {output_file}")
    
    # Convert results to JSON
    results_dict = results.to_dict()
    
    with open(output_file, 'w') as f:
        json.dump(results_dict, f, indent=2)
    
    print(f"✅ Results saved to {output_file}")

def print_summary(results):
    """Print evaluation summary"""
    print("\n" + "="*60)
    print("📊 RAGAS Evaluation Results")
    print("="*60)
    
    # Convert to DataFrame for better visualization
    df = results.to_pandas()
    
    # Print metrics summary
    print("\n📈 Metrics Summary:")
    print("-" * 60)
    
    metrics_cols = ['faithfulness', 'answer_relevancy', 'context_precision', 
                    'context_recall', 'answer_correctness']
    
    for col in metrics_cols:
        if col in df.columns:
            mean = df[col].mean()
            std = df[col].std()
            print(f"  {col:25} → Mean: {mean:.4f} (±{std:.4f})")
    
    print("\n" + "="*60)
    
    # Print per-sample results
    print("\n📝 Per-Sample Results:")
    print("-" * 60)
    print(df[metrics_cols].round(4).to_string())
    print("\n" + "="*60)

def main():
    """Main evaluation function"""
    print("="*60)
    print("🧪 RAG Evaluation Tool")
    print("="*60)
    
    # Load data
    data = load_evaluation_data()
    if data is None:
        print("\n💡 To run evaluation:")
        print("1. Generate Q&A responses from your RAG system")
        print("2. Save results to outputs/evaluation_data.json with format:")
        print("   {")
        print('       "questions": [...],')
        print('       "answers": [...],')
        print('       "contexts": [...],')
        print('       "ground_truths": [...]')
        print("   }")
        return
    
    # Prepare dataset
    dataset = prepare_dataset(data)
    
    # Run evaluation
    results = run_evaluation(dataset)
    if results is None:
        return
    
    # Save results
    save_results(results)
    
    # Print summary
    print_summary(results)

if __name__ == "__main__":
    main()
