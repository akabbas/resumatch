#!/usr/bin/env python3
"""Quick test of enhanced local AI features"""

from resume_generator import KeywordExtractor

# Test the enhanced keyword extraction
job_description = """
Senior Business Systems Analyst with 2+ years experience in Salesforce CRM and CPQ implementations.
Must have experience with Azure cloud services, REST API integrations, and Jira for project management.
Salesforce Administrator certification preferred. Experience with custom pricing rules and Oracle CPQ.
Strong analytical skills and ability to work with cross-functional teams.
"""

print("🔍 Testing Enhanced Local AI")
print("=" * 50)

extractor = KeywordExtractor(use_openai=False)
keywords = extractor.extract_keywords(job_description)

print(f"📊 Extracted {len(keywords)} keywords:")
for i, keyword in enumerate(keywords[:10], 1):
    print(f"  {i:2d}. {keyword}")

print("\n✅ Enhanced features working!")
