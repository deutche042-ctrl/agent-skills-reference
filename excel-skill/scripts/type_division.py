#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generic text-content classification & statistics script.
(This is a template: replace the placeholder keyword/category names below
with the real domain keywords for your task.)
"""

import pandas as pd
import re
from collections import Counter

# Read the data
df = pd.read_excel('/path/to/input_file.xlsx')

# Define the classification keyword mapping
# Based on an analysis of the text content, define the classification rules

def extract_specific_issues(content, case_type):
    """
    Extract classification issues from the text content.
    Returns a list of issues (a single text may contain multiple issues).
    """
    issues = []
    content = str(content)

    # ============ category1-related issues ============
    if any(kw in content for kw in ['keyword1', 'keyword2', 'keyword3', 'keyword4', 'keyword5', 'keyword6']):
        issues.append('category1-subcategory1')
    elif any(kw in content for kw in ['keyword7', 'keyword8', 'keyword9', 'keyword10', 'keyword11']):
        issues.append('category1-subcategory2')
    elif any(kw in content for kw in ['keyword12', 'keyword13', 'keyword14']):
        if 'keyword1' not in content and 'keyword2' not in content:
            issues.append('category1-subcategory3')
    elif 'keyword15' in content and not issues:
        # other category1-related
        if 'keyword16' in content:
            issues.append('category1-subcategory4')
        elif 'keyword17' in content or 'keyword18' in content:
            issues.append('category1-subcategory5')
        else:
            issues.append('category1-subcategory1')

    # ============ category2-related issues ============
    if any(kw in content for kw in ['keyword19', 'keyword20']):
        if any(kw in content for kw in ['keyword21', 'keyword22', 'keyword23', 'keyword24', 'keyword25']):
            issues.append('category2-subcategory1')
        elif 'keyword26' in content:
            issues.append('category2-subcategory2')
        else:
            issues.append('category2-subcategory3')

    # ============ category3-related issues ============
    if any(kw in content for kw in ['keyword27', 'keyword28', 'keyword29']):
        if any(kw in content for kw in ['keyword21', 'keyword22', 'keyword23', 'keyword24']):
            issues.append('category3-subcategory1')
        elif 'keyword30' in content or 'keyword31' not in content and 'keyword32' in content:
            issues.append('category3-subcategory2')
        else:
            issues.append('category3-subcategory3')

    # ============ category4-related issues ============
    if 'keyword33' in content:
        if any(kw in content for kw in ['keyword21', 'keyword22', 'keyword23']):
            issues.append('category4-subcategory1')
        elif 'keyword34' in content:
            issues.append('category4-subcategory2')
        elif 'keyword35' in content or 'keyword36' in content:
            issues.append('category4-subcategory3')
        else:
            issues.append('category4-subcategory4')

    # ============ category5-related issues ============
    if any(kw in content for kw in ['keyword37', 'keyword38', 'keyword39']):
        if any(kw in content for kw in ['keyword21', 'keyword22', 'keyword23', 'keyword24']):
            issues.append('category5-subcategory1')
        else:
            issues.append('category5-subcategory2')

    # ============ category6-related issues ============
    if any(kw in content for kw in ['keyword40', 'keyword41', 'keyword42']):
        issues.append('category6-subcategory1')

    # ============ category7-related issues ============
    if any(kw in content for kw in ['keyword43', 'keyword44', 'keyword45']):
        if any(kw in content for kw in ['keyword46', 'keyword47', 'keyword22', 'keyword23', 'keyword24']):
            issues.append('category7-subcategory1')
        else:
            issues.append('category7-subcategory2')

    # ============ category8-related issues ============
    if any(kw in content for kw in ['keyword48', 'keyword49', 'keyword50']):
        if 'keyword51' in content or 'keyword52' in content:
            issues.append('category8-subcategory1')
        else:
            issues.append('category8-subcategory2')

    # ============ category9-related issues ============
    if any(kw in content for kw in ['keyword53', 'keyword54', 'keyword55']):
        if 'keyword56' in content or 'keyword57' in content or 'keyword58' in content:
            issues.append('category9-subcategory1')
        elif 'keyword59' in content:
            if 'keyword37' not in str(issues):
                issues.append('category9-subcategory2')

    # ============ category10-related issues ============
    if any(kw in content for kw in ['keyword60', 'keyword61', 'keyword62']):
        issues.append('category10-subcategory1')
    if any(kw in content for kw in ['keyword63', 'keyword64']):
        if 'keyword65' in content or 'keyword66' in content or 'keyword67' in content:
            issues.append('category10-subcategory2')

    # ============ category11-related issues ============
    if any(kw in content for kw in ['keyword68', 'keyword69', 'keyword70']):
        issues.append('category11-subcategory1')

    # ============ category12-related issues ============
    if any(kw in content for kw in ['keyword71', 'keyword72', 'keyword73']):
        if 'keyword74' in content:
            issues.append('category12-subcategory1')
        else:
            issues.append('category12-subcategory2')

    # ============ category13-related issues ============
    if 'keyword75' in content:
        if 'keyword76' in content or 'keyword77' in content:
            issues.append('category13-subcategory1')
        elif 'keyword78' in content or 'keyword79' in content:
            issues.append('category13-subcategory2')

    # ============ category14-related issues ============
    if any(kw in content for kw in ['keyword80', 'keyword81']):
        issues.append('category14-subcategory1')

    # ============ category15-related issues ============
    if any(kw in content for kw in ['keyword82', 'keyword83', 'keyword84']):
        issues.append('category15-subcategory1')

    # ============ category16-related issues ============
    if any(kw in content for kw in ['keyword85', 'keyword86', 'keyword87']):
        issues.append('category16-subcategory1')

    # ============ category17-related issues ============
    if 'keyword88' in content and 'keyword15' not in content:
        issues.append('category17-subcategory1')

    # ============ category18-related issues ============
    if any(kw in content for kw in ['keyword89', 'keyword90', 'keyword91']):
        issues.append('category18-subcategory1')

    # ============ category19-related issues ============
    if any(kw in content for kw in ['keyword92', 'keyword93', 'keyword94']):
        issues.append('category19-subcategory1')

    # ============ category20-related issues ============
    if any(kw in content for kw in ['keyword95', 'keyword96', 'keyword97', 'keyword98']):
        issues.append('category20-subcategory1')

    # ============ category21-related issues ============
    if 'keyword99' in content and 'keyword15' not in content:
        issues.append('category21-subcategory1')

    # ============ category22-related issues ============
    if 'keyword100' in content and not issues:
        if 'keyword15' in content:
            issues.append('category22-subcategory1')
        elif 'keyword33' in content:
            issues.append('category22-subcategory2')
        else:
            issues.append('category22-subcategory3')

    # ============ category23-related issues ============
    if any(kw in content for kw in ['keyword101', 'keyword102', 'keyword103']):
        issues.append('category23-subcategory1')

    # If no specific issue was identified, give a default classification based on the case type
    if not issues:
        if case_type == 'type1':
            issues.append('category24-subcategory1')
        elif case_type == 'type2':
            issues.append('category24-subcategory2')
        elif case_type == 'type3':
            issues.append('category24-subcategory3')
        elif case_type == 'type4':
            issues.append('category24-subcategory4')
        elif case_type == 'type5':
            issues.append('category24-subcategory5')
        elif case_type == 'type6':
            issues.append('category24-subcategory6')
        elif case_type == 'type7':
            issues.append('category24-subcategory7')
        elif case_type == 'type8':
            issues.append('category24-subcategory8')
        else:
            issues.append('category25')

    return issues


# Extract the specific issues from all texts
all_issues = []
issue_details = []

for idx, row in df.iterrows():
    content = row['text_content']
    case_type = row['type']
    issues = extract_specific_issues(content, case_type)

    for issue in issues:
        all_issues.append(issue)
        issue_details.append({
            'id': row['id'],
            'type': case_type,
            'specific_issue': issue,
            'text_summary': str(content)[:100] + '...' if len(str(content)) > 100 else content
        })

# Count the specific issues
issue_counts = Counter(all_issues)

# Output the statistics
print("=" * 60)
print("Text content classification statistics")
print("=" * 60)
print(f"\nTotal text records: {len(df)}")
print(f"Total specific issues identified: {len(all_issues)}")
print(f"Number of specific-issue categories: {len(issue_counts)}")

print("\n" + "-" * 60)
print("Specific-issue classification statistics (descending by count)")
print("-" * 60)

for issue, count in issue_counts.most_common():
    print(f"{issue}: {count} records")

# Build the detailed DataFrame
details_df = pd.DataFrame(issue_details)

# Save the results
details_df.to_excel('/path/to/output_details.xlsx', index=False)

# Build the statistics summary table
summary_data = []
for issue, count in issue_counts.most_common():
    summary_data.append({
        'specific_issue': issue,
        'count': count,
        'percentage': f'{count/len(all_issues)*100:.1f}%'
    })

summary_df = pd.DataFrame(summary_data)
summary_df.to_excel('/path/to/output_summary.xlsx', index=False)

print("\n" + "=" * 60)
print("Results saved to:")
print("1. /path/to/output_details.xlsx")
print("2. /path/to/output_summary.xlsx")
print("=" * 60)
