"""Programmatic verification of Savexa API workflows and OOD rejection."""

from __future__ import annotations

import json
import urllib.request
import urllib.error
from pathlib import Path

# Paths to test images
TEST_DIR = Path(__file__).parents[1] / "dataset_clean" / "test"
NEG_DIR = Path(__file__).parents[1] / "evaluation" / "negative_images"

TEST_CASES = [
    {
        "name": "Burn Upload",
        "type": "detect",
        "file": TEST_DIR / "Burn" / "30d0452526e77c96.jpg",
        "expected_injury": "Burn",
        "expected_valid": True
    },
    {
        "name": "Cut Upload",
        "type": "detect",
        "file": TEST_DIR / "Cut" / "02b1d01d7e507ddb.jpg",
        "expected_injury": "Cut",
        "expected_valid": True
    },
    {
        "name": "Abrasion Upload",
        "type": "detect",
        "file": TEST_DIR / "Abrasions" / "21cddca7a08a61d0.jpg",
        "expected_injury": "Abrasions",
        "expected_valid": True
    },
    {
        "name": "Bruise Upload",
        "type": "detect",
        "file": TEST_DIR / "Bruises" / "0158b13e2ff10b16.jpg",
        "expected_injury": "Bruises",
        "expected_valid": True
    },
    {
        "name": "Laceration Upload",
        "type": "detect",
        "file": TEST_DIR / "Laceration" / "2fb703091dbbbe49.jpg",
        "expected_injury": "Laceration",
        "expected_valid": True
    },
    {
        "name": "Stab wound Upload",
        "type": "detect",
        "file": TEST_DIR / "Stab_wound" / "132a04c13bf5c343.jpg",
        "expected_injury": "Stab_wound",
        "expected_valid": True
    },
    {
        "name": "Animal bite Upload",
        "type": "detect",
        "file": TEST_DIR / "Animal_bite" / "0008a85299b3e73c.png",
        "expected_injury": "Animal_bite",
        "expected_valid": True
    },
    {
        "name": "Unclear / Non-injury image",
        "type": "detect",
        "file": NEG_DIR / "Screenshot 2026-08-24 203849.png",
        "expected_injury": "OOD Rejection",
        "expected_valid": False
    },
    {
        "name": "Chatbot Burn Question",
        "type": "chat",
        "message": "how to treat a burn",
        "expected_contains": "Burn"
    },
    {
        "name": "Chatbot General Question",
        "type": "chat",
        "message": "hello",
        "expected_contains": "first-aid guidance"
    }
]


def encode_multipart_formdata(fields, files):
    boundary = b'----WebKitFormBoundary7MA4YWxkTrZu0gW'
    lines = []
    for name, value in fields.items():
        lines.extend([
            b'--' + boundary,
            f'Content-Disposition: form-data; name="{name}"'.encode('utf-8'),
            b'',
            str(value).encode('utf-8')
        ])
    for name, filepath in files.items():
        path = Path(filepath)
        filename = path.name
        content_type = "image/png" if path.suffix.lower() == ".png" else "image/jpeg"
        with open(path, "rb") as f:
            file_content = f.read()
        lines.extend([
            b'--' + boundary,
            f'Content-Disposition: form-data; name="{name}"; filename="{filename}"'.encode('utf-8'),
            f'Content-Type: {content_type}'.encode('utf-8'),
            b'',
            file_content
        ])
    lines.append(b'--' + boundary + b'--')
    lines.append(b'')
    body = b'\r\n'.join(lines)
    headers = {'Content-Type': f'multipart/form-data; boundary={boundary.decode("utf-8")}'}
    return body, headers


def main():
    print("Starting Savexa API workflow testing...\n")
    
    results = []
    
    for case in TEST_CASES:
        name = case["name"]
        print(f"Running test case: {name}...")
        
        if case["type"] == "detect":
            # Test image upload and classification
            filepath = case["file"]
            if not filepath.exists():
                print(f"  [ERROR] File not found: {filepath}")
                results.append((name, str(filepath.name), "File not found", "ERROR", "FAIL"))
                continue
                
            body, headers = encode_multipart_formdata({}, {"image": filepath})
            req = urllib.request.Request("http://127.0.0.1:8000/api/detect/", data=body, headers=headers, method="POST")
            
            try:
                with urllib.request.urlopen(req) as response:
                    resp_data = json.loads(response.read().decode("utf-8"))
                    
                actual_injury = resp_data.get("injury_type")
                actual_valid = resp_data.get("valid")
                similarity = resp_data.get("similarity")
                
                # Check results
                if case["expected_valid"]:
                    passed = (actual_injury == case["expected_injury"]) and (actual_valid is True)
                    expected_str = f"Injury: {case['expected_injury']}, Valid: True"
                    actual_str = f"Injury: {actual_injury}, Valid: {actual_valid} (Similarity: {similarity})"
                else:
                    passed = (actual_valid is False)
                    expected_str = "Valid: False"
                    actual_str = f"Valid: {actual_valid} (Similarity: {similarity}, Predicted class: {actual_injury})"
                    
                status = "PASS" if passed else "FAIL"
                results.append((name, str(filepath.name), expected_str, actual_str, status))
                print(f"  Result: {status} (Expected: {expected_str} | Actual: {actual_str})")
                
            except Exception as e:
                print(f"  [ERROR] Request failed: {e}")
                results.append((name, str(filepath.name), "Success response", f"Exception: {e}", "FAIL"))
                
        elif case["type"] == "chat":
            # Test chatbot response
            message = case["message"]
            post_data = json.dumps({"message": message}).encode("utf-8")
            headers = {"Content-Type": "application/json"}
            req = urllib.request.Request("http://127.0.0.1:8000/api/chat/", data=post_data, headers=headers, method="POST")
            
            try:
                with urllib.request.urlopen(req) as response:
                    resp_data = json.loads(response.read().decode("utf-8"))
                    
                answer = resp_data.get("answer", "")
                passed = case["expected_contains"].lower() in answer.lower()
                expected_str = f"Contains '{case['expected_contains']}'"
                actual_str = f"Answer starts with: '{answer[:80]}...'"
                
                status = "PASS" if passed else "FAIL"
                results.append((name, f"Msg: {message}", expected_str, actual_str, status))
                print(f"  Result: {status} (Expected: {expected_str} | Actual: {actual_str})")
                
            except Exception as e:
                print(f"  [ERROR] Request failed: {e}")
                results.append((name, f"Msg: {message}", "Success response", f"Exception: {e}", "FAIL"))
                
    # Print Markdown Table
    print("\n\n### Workflow Test Results Table\n")
    print("| Test Case | Input | Expected Output | Actual Output | Status |")
    print("| --- | --- | --- | --- | --- |")
    for row in results:
        print(f"| {row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]} |")
    print("\nDone.")


if __name__ == "__main__":
    main()
