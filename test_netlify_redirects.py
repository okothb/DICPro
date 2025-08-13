#!/usr/bin/env python3
"""
Test script to verify Netlify redirect configuration
Simulates how Netlify will handle different URL requests
"""

import re
from pathlib import Path

def parse_netlify_toml():
    """Parse the netlify.toml file and extract redirect rules"""
    toml_path = Path("netlify.toml")
    
    if not toml_path.exists():
        print("❌ netlify.toml not found")
        return []
    
    content = toml_path.read_text()
    
    # Extract redirect rules
    redirects = []
    lines = content.split('\n')
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line == '[[redirects]]':
            # Parse redirect block
            redirect = {}
            i += 1
            while i < len(lines) and not lines[i].strip().startswith('[['):
                line = lines[i].strip()
                if line.startswith('from = '):
                    redirect['from'] = line.split('=', 1)[1].strip().strip('"')
                elif line.startswith('to = '):
                    redirect['to'] = line.split('=', 1)[1].strip().strip('"')
                elif line.startswith('status = '):
                    redirect['status'] = int(line.split('=', 1)[1].strip())
                i += 1
            
            if 'from' in redirect and 'to' in redirect:
                redirects.append(redirect)
        else:
            i += 1
    
    return redirects

def test_redirect_rules():
    """Test various URL patterns against redirect rules"""
    print("🔍 Testing Netlify Redirect Configuration")
    print("=" * 50)
    
    redirects = parse_netlify_toml()
    
    if not redirects:
        print("❌ No redirects found in netlify.toml")
        return False
    
    print(f"📋 Found {len(redirects)} redirect rules:")
    for i, redirect in enumerate(redirects, 1):
        status_type = "Rewrite" if redirect.get('status') == 200 else "Redirect"
        print(f"  {i}. {redirect['from']} → {redirect['to']} ({status_type})")
    
    print("\n🧪 Testing URL Patterns:")
    
    # Test cases
    test_cases = [
        {
            'url': '/',
            'expected': '/landing.html',
            'description': 'Root URL should serve landing page'
        },
        {
            'url': '/home',
            'expected': '/landing.html',
            'description': 'Home URL should serve landing page'
        },
        {
            'url': '/landing',
            'expected': '/landing.html',
            'description': 'Landing URL should serve landing page'
        },
        {
            'url': '/app',
            'expected': '/index.html',
            'description': 'App URL should serve main application'
        },
        {
            'url': '/index.html',
            'expected': '/index.html',
            'description': 'Direct index.html access should work'
        },
        {
            'url': '/api/health',
            'expected': '/.netlify/functions/api/health',
            'description': 'API calls should route to functions'
        },
        {
            'url': '/protect',
            'expected': '/.netlify/functions/api/protect',
            'description': 'Direct API endpoints should work'
        }
    ]
    
    passed = 0
    total = len(test_cases)
    
    for test in test_cases:
        url = test['url']
        expected = test['expected']
        description = test['description']
        
        # Find matching redirect
        matched_redirect = None
        for redirect in redirects:
            from_pattern = redirect['from']
            
            # Handle wildcard patterns
            if from_pattern.endswith('/*'):
                pattern = from_pattern[:-2]
                if url.startswith(pattern):
                    # Handle splat replacement
                    to_pattern = redirect['to']
                    if ':splat' in to_pattern:
                        remaining = url[len(pattern):]
                        if remaining.startswith('/'):
                            remaining = remaining[1:]
                        actual = to_pattern.replace(':splat', remaining)
                    else:
                        actual = to_pattern
                    matched_redirect = {'to': actual, 'status': redirect.get('status', 302)}
                    break
            elif from_pattern == url:
                matched_redirect = redirect
                break
        
        if matched_redirect:
            actual = matched_redirect['to']
            status = matched_redirect.get('status', 302)
            
            if actual == expected:
                print(f"  ✅ {url} → {actual} ({status}) - {description}")
                passed += 1
            else:
                print(f"  ❌ {url} → {actual} (expected {expected}) - {description}")
        else:
            print(f"  ⚠️  {url} → No redirect rule found - {description}")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All redirect tests PASSED! Landing page is properly configured as first point of contact.")
        return True
    else:
        print(f"⚠️  {total - passed} tests failed. Check redirect configuration.")
        return False

def verify_file_structure():
    """Verify that required files exist"""
    print("\n📁 Verifying File Structure:")
    
    required_files = [
        'web/landing.html',
        'web/index.html',
        'netlify/functions/api.py',
        'netlify.toml'
    ]
    
    all_exist = True
    
    for file_path in required_files:
        path = Path(file_path)
        if path.exists():
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path} - Missing!")
            all_exist = False
    
    return all_exist

def main():
    """Run all tests"""
    print("🚀 Netlify Configuration Verification")
    print("=" * 60)
    
    # Test file structure
    files_ok = verify_file_structure()
    
    # Test redirects
    redirects_ok = test_redirect_rules()
    
    print("\n" + "=" * 60)
    
    if files_ok and redirects_ok:
        print("🎉 CONFIGURATION VERIFIED!")
        print("✅ Landing page is properly set as the first point of contact")
        print("✅ All redirect rules are working correctly")
        print("✅ File structure is complete")
        print("\n🚀 Ready for deployment with: netlify deploy --prod")
        return True
    else:
        print("❌ CONFIGURATION ISSUES FOUND")
        if not files_ok:
            print("⚠️  Missing required files")
        if not redirects_ok:
            print("⚠️  Redirect configuration issues")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)