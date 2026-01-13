import pandas as pd
import json
import os
import glob
import math

# Configuration
DATA_DIR = 'data_files'
OUTPUT_FILE = 'data.json'

# MAPPINGS
CITY_MAP = {
    'ירושלים': 'jerusalem',
    'תל אביב - יפו': 'telaviv',
    'תל אביב יפו': 'telaviv',
    'חיפה': 'haifa',
    'באר שבע': 'beersheva',
    'פתח תקווה': 'petah_tikva'
}

OFFENSE_MAP = {
    # Assault / Violence
    'תגרה': 'assault',
    'תקיפה': 'assault',
    'אלימות פיזית': 'assault',
    'תקיפה הגורמת חבלה ממש': 'assault',
    'תקיפה סתם': 'assault',
    'תקיפה סתם ע\'י שניים או יותר': 'assault',
    'תקיפה במקום בו מתקיים אירוע ספורט': 'assault',
    'תקיפה וחבלה ממשית ע\'י שניים או יותר': 'assault',
    'חבלה ע\'י שניים או יותר': 'assault',
    'חבלה חמורה': 'assault',
    'אלימות בספורט': 'assault',
    'תקיפת קטין וגרימת חבלה של ממש': 'assault',

    # Banned Items
    'החזקת סכין': 'banned_item',
    'הכנסת חפץ אסור': 'banned_item',
    'איסור הכנסת חפץ אסור לאירוע ספורט': 'banned_item',
    'הכנסת חפץ לאירוע ספורט המפורט בתוספת השלישית': 'banned_item',
    'החזקת אגרופן או סכין שלא כדין': 'banned_item',
    'איסור הכנסת חפץ אסור מסוג מכלול האמצעים הכימיים שה': 'banned_item',
    'איסור ידויי חפץ': 'banned_item',
    'רכישה, נשיאה או הובלת נשק בלא רשות על פי דין': 'banned_item',
    'החזקת חלק, אבזר או תחמושת שאינם חלק מהותי בנשק': 'banned_item',

    # Pyrotechnics
    'שימוש בחומר נפיץ': 'pyro',
    'אבוקות': 'pyro',
    'זיקוקין': 'pyro',
    'שמוש פחזני באש או בחומר דליק': 'pyro',
    'הפעלת נשק או זיקוקין בדרך צבורית': 'pyro',
    'גרימת פיצוץ חומר נפץ': 'pyro',
    'הנחת חומר נפיץ או נוזל שלא כדין': 'pyro',
    'שיגור חומר נפיץ לאחר שלא כדין': 'pyro',
    'נסיון לחבול בחומר נפיץ': 'pyro',
    'היזק מכוון בחומר נפיץ': 'pyro',
    'טפול בלתי זהיר בחומר נפץ': 'pyro',
    'הצתה': 'pyro',

    # Police
    'תקיפת שוטר': 'police',
    'הפרעה לשוטר': 'police',
    'תקיפת שוטר בעת מלוי תפקידו': 'police',
    'תקיפת שוטר כשהתוקף מזוין בנשק חם/קר': 'police',
    'תקיפת שוטר כדי להכשילו בתפקידו': 'police',
    'תקיפת שוטר ע\'י שלושה או יותר': 'police',
    'הפרעת שוטר במלוי תפקידו': 'police',
    'הפרעה לשוטר בנסיבות מחמירות': 'police',
    'העלבת עובד ציבור': 'police', # Often grouped
    'הפרעה לעובד ציבור': 'police',
    'תקיפת עובד ציבור': 'police',

    # Public Order
    'הפרת הסדר הציבורי': 'order',
    'התנהגות פרועה במקום צבורי': 'order',
    'התנהגות העלולה להפר שלום הציבור': 'order',
    'מהומה במקום ציבורי': 'order',
    'השתתפות בהתפרעות': 'order',
    
    # Field Invasion
    'כניסה לשדה המשחק': 'field',
    'איסור כניסה למקום': 'field',
    'איסור כניסה לשדה המשחק': 'field',
    'הסגת גבול פלילית': 'field',

    # Property
    'היזק לרכוש': 'property',
    'היזק לרכוש במזיד': 'property',
    'חבלה במזיד ברכב': 'property',
    'יידוי אבן/חפץ לעבר רכב במטרה לפגוע': 'property',

    # Threats / Other
    'איומים': 'threat',
    'גניבה': 'other',
    'החזקת נכס חשוד כגנוב': 'other',
    'קשירת קשר לעשות פשע': 'other',
    'שיבוש מהלכי משפט': 'other',
    'התחזות כאדם אחר במטרה להונות': 'other',
    'הפרת הוראה חוקית': 'other'
}

# Age Bins
def get_age_group(age):
    if pd.isna(age): return 'Unknown'
    age = int(age)
    if 13 <= age <= 17: return '13-17'
    if 18 <= age <= 21: return '18-21'
    if 22 <= age <= 25: return '22-25'
    if 26 <= age <= 30: return '26-30'
    if 31 <= age <= 40: return '31-40'
    if 41 <= age <= 50: return '41-50'
    if age > 50: return '50+'
    return 'Other'

DEFAULT_GROUPS = ['13-17', '18-21', '22-25', '26-30', '31-40', '41-50', '50+']

def process_arrests(filepath):
    """Processes a single arrests Excel file."""
    print(f"Processing arrests file: {filepath}")
    
    # 1. Read Arrests Clean Sheet
    try:
        df = pd.read_excel(filepath, sheet_name=0) # Assuming first sheet is always 'מעצרים נקי' or similar
    except Exception as e:
        print(f"Error reading first sheet of {filepath}: {e}")
        return [], 0
        
    # Standardize columns
    # We found: ['תאריך מעצר', 'תאור סמל חוק', 'עבירה', 'גיל', 'ישוב עבירה מחושב', 'Column1']
    # Mapping to standard names
    df.rename(columns={
        'ישוב עבירה מחושב': 'city_he',
        'עבירה': 'offense_he',
        'גיל': 'age',
        'גיל': 'age',
        'תאור סמל חוק': 'law_desc',
        'Column1': 'quantity', # The quantity column
        'תאריך מעצר': 'date'
    }, inplace=True)
    
    processed_records = []
    
    for _, row in df.iterrows():
        city_he = str(row.get('city_he', '')).strip()
        offense_he = str(row.get('offense_he', '')).strip()
        law_desc = str(row.get('law_desc', '')).strip()
        age = row.get('age')
        
        # Extract Year
        date_val = row.get('date')
        year = None
        if pd.notna(date_val):
            try:
                year = pd.to_datetime(date_val).year
            except:
                pass
        
        # Get Quantity (default 1)
        qty = 1
        raw_qty = row.get('quantity')
        if pd.notna(raw_qty):
            try:
                qty = int(float(raw_qty))
            except:
                qty = 1
        
        # Filter outlier (User request)
        if qty > 200: 
            print(f"Skipping outlier row with quantity {qty}")
            continue
        
        # Map City
        city_key = CITY_MAP.get(city_he, 'other')
        if city_key == 'other':
            # Try partial matching or specific known issues
            pass
            
        # Map Offense
        offense_key = OFFENSE_MAP.get(offense_he, 'other')
        
        # Fallback to law description if offense is generic or not found
        if offense_key == 'other':
            for key, val in OFFENSE_MAP.items():
                if key in law_desc:
                    offense_key = val
                    break
            
            # Special case for Sports Violence Law
            if 'איסור אלימות בספורט' in law_desc:
                 # If we still don't know, assume it's relevant to order or banned items, 
                 # but usually specific offenses are listed. Let's map general "Violence in Sport" law to 'order' if nothing else matches.
                 if offense_key == 'other':
                     offense_key = 'order'

        # If still 'other' and it's not a general 'other' (like theft), we might want to log it?
        # For now, we keep it.
        
        processed_records.append({
            'city': city_key,
            'offense': offense_key,
            'age_group': get_age_group(age),
            'weight': qty, # Add weight
            'year': year # Add year
        })
        
        if 'חיפה' in city_he and city_key == 'haifa':
             pass
        
    # 2. Read Indictments Sheet (for total gap model)
    total_indictments = 0
    try:
        df_indict = pd.read_excel(filepath, sheet_name='כתבי אישום')
        # Look for the total row or sum the column
        # Found column: 'כמות תיקים עם כ"א לפי תאריך כתב אישום'
        col_name = 'כמות תיקים עם כ"א לפי תאריך כתב אישום'
        if col_name in df_indict.columns:
             # Usually row 0 is total, but safer to sum numeric values excluding the 'Total' text row if present
             # In inspection: row 0 was "סה"כ" with value 57.
             # Let's filter for year rows or just take the explicit total if we can identify it.
             # Actually, simpler: Sum all rows where 'שנת כתב אישום' is a number
             
             # Converting to numeric, coercing errors to NaN
             df_indict[col_name] = pd.to_numeric(df_indict[col_name], errors='coerce')
             
             # If we trust the "Total" row exists and is correct:
             total_row = df_indict[df_indict['שנת כתב אישום'].astype(str).str.contains('סה"כ', na=False)]
             if not total_row.empty:
                 total_indictments = total_row.iloc[0][col_name]
             else:
                 total_indictments = df_indict[col_name].sum()
    except Exception as e:
        print(f"Warning: Could not read Indictments sheet in {filepath}: {e}")

    return processed_records, total_indictments

def process_extra_sheets(filepath):
    """Processes optional sheets for status and closing grounds."""
    meta_stats = {
        'status_counts': {},
        'closing_counts': {}
    }
    
    # 1. Status Sheet
    try:
        df_status = pd.read_excel(filepath, sheet_name='סטטוס תיק נקי')
        col = 'סטטוס תיק כולל החלטה שיפוטית'
        if col in df_status.columns:
            # Filter NaNs and empty strings
            valid_stats = df_status[col].dropna().astype(str)
            valid_stats = valid_stats[valid_stats.str.strip() != '']
            counts = valid_stats.value_counts().to_dict()
            meta_stats['status_counts'] = counts
    except Exception:
        pass # Sheet might not exist
        
    # 2. Closing Grounds Sheet
    try:
        df_closing = pd.read_excel(filepath, sheet_name='עילות סגירת תיק נקי')
        col = 'תאור סיבת סגירת תיק'
        if col in df_closing.columns:
             # Filter NaNs and empty strings
            valid_closing = df_closing[col].dropna().astype(str)
            valid_closing = valid_closing[valid_closing.str.strip() != '']
            counts = valid_closing.value_counts().to_dict()
            meta_stats['closing_counts'] = counts
    except Exception:
        pass
        
    return meta_stats

def process_indictment_stats(filepath):
    """
    Processes the 'Status' sheet to calculate Indictment Rate per Offense.
    Indictment = 'פרקליטות-תביעות' or 'החלטה שיפוטית'
    """
    stats = {}
    
    try:
        df = pd.read_excel(filepath, sheet_name='סטטוס תיק נקי')
        
        # Standardize columns (same as arrests sheet)
        df.rename(columns={
            'עבירה': 'offense_he',
            'תאור סמל חוק': 'law_desc',
            'סטטוס תיק כולל החלטה שיפוטית': 'status'
        }, inplace=True)
        
        # Initialize stats for known offenses
        known_offenses = list(set(OFFENSE_MAP.values()))
        stats = {off: {'total': 0, 'indict': 0} for off in known_offenses}
        stats['other'] = {'total': 0, 'indict': 0} # Catch-all
        
        for _, row in df.iterrows():
            offense_he = str(row.get('offense_he', '')).strip()
            law_desc = str(row.get('law_desc', '')).strip()
            status = str(row.get('status', '')).strip()
            
            # Map Offense
            offense_key = OFFENSE_MAP.get(offense_he, 'other')
            if offense_key == 'other':
                # Fallback to law description
                for key, val in OFFENSE_MAP.items():
                    if key in law_desc:
                        offense_key = val
                        break
                if 'איסור אלימות בספורט' in law_desc and offense_key == 'other':
                    offense_key = 'order' # Default for general sports violence law
            
            # Determine Indictment Status
            is_indictment = status in ['פרקליטות-תביעות', 'החלטה שיפוטית']
            
            # Update stats
            if offense_key in stats:
                stats[offense_key]['total'] += 1
                if is_indictment:
                    stats[offense_key]['indict'] += 1
            else:
                 # Should be caught by 'other', but safety check
                 pass

    except Exception as e:
        print(f"Error processing Indictment Stats: {e}")
        
    return stats

def process_closing_reason_stats(filepath):
    """
    Processes 'Closing Reasons' sheet to aggregate reasons by offense.
    Key insight: "Lack of Evidence" vs "Lack of Guilt" vs "Other" per offense.
    """
    stats = {}
    try:
        df = pd.read_excel(filepath, sheet_name='עילות סגירת תיק נקי')
        
        # Renaissance columns
        df.rename(columns={
            'עבירה': 'offense_he',
            'תאור סמל חוק': 'law_desc',
            'תאור סיבת סגירת תיק': 'reason'
        }, inplace=True)
        
        # Init stats
        known_offenses = list(set(OFFENSE_MAP.values()))
        # Structure: offense -> { reason_category -> count }
        stats = {off: {'total': 0, 'lack_evidence': 0, 'lack_guilt': 0, 'other': 0} for off in known_offenses}
        stats['other'] = {'total': 0, 'lack_evidence': 0, 'lack_guilt': 0, 'other': 0}

        for _, row in df.iterrows():
            offense_he = str(row.get('offense_he', '')).strip()
            law_desc = str(row.get('law_desc', '')).strip()
            reason = str(row.get('reason', '')).strip()
            
            # Map Offense (Reuse logic - could refactor to helper but extensive enough here)
            offense_key = OFFENSE_MAP.get(offense_he, 'other')
            if offense_key == 'other':
                 for key, val in OFFENSE_MAP.items():
                    if key in law_desc:
                        offense_key = val
                        break
                 if 'איסור אלימות בספורט' in law_desc and offense_key == 'other':
                    offense_key = 'order'

            # Map Reason
            category = 'other'
            if 'חוסר ראיות' in reason:
                category = 'lack_evidence'
            elif 'חוסר אשמה' in reason:
                category = 'lack_guilt'
            
            # Update
            if offense_key in stats:
                stats[offense_key]['total'] += 1
                stats[offense_key][category] += 1
    
    except Exception as e:
        print(f"Error processing Closing Stats: {e}")
        
    return stats

def aggregate_data(all_records):
    """Aggregates raw records into the structure required by Chart.js"""
    
    # Structure:
    # city -> offense -> { data: [%, %, ...], counts: [n, n, ...], total: N, text: "..." }
    
    # Initialize
    output = {}
    cities = ['all'] + list(CITY_MAP.values())
    offenses = ['all'] + list(set(OFFENSE_MAP.values()))
    
    # Helper to init a node
    def init_node():
        return {
            'counts': {g: 0 for g in DEFAULT_GROUPS},
            'total': 0
        }

    # Build hierarchy
    tree = {c: {o: init_node() for o in offenses} for c in cities}
    
    for r in all_records:
        c = r['city']
        o = r['offense']
        g = r['age_group']
        
        w = r.get('weight', 1) # Get weight
        
        # Skip unknown age groups for chart clarity? Or keep them? 
        # The chart expects specific labels. Let's map 'Other' or 'Unknown' to nothing or handle them.
        if g not in DEFAULT_GROUPS: continue

        # Add to specific City & specific Offense
        if c in tree: # valid city
             if o in tree[c]:
                 tree[c][o]['counts'][g] += w
                 tree[c][o]['total'] += w
             # Add to 'all' offenses for this city
             tree[c]['all']['counts'][g] += w
             tree[c]['all']['total'] += w
        
        # Add to 'all' Cities
        if o in tree['all']:
             tree['all'][o]['counts'][g] += w
             tree['all'][o]['total'] += w
        # Add to 'all' Cities & 'all' Offenses
        tree['all']['all']['counts'][g] += w
        tree['all']['all']['total'] += w

    # Convert to final lists
    final_output = {}
    for city, offenses_data in tree.items():
        final_output[city] = {}
        for offense, node in offenses_data.items():
            total = node['total']
            counts_list = [node['counts'][g] for g in DEFAULT_GROUPS]
            if total > 0:
                data_list = [round((x / total) * 100, 1) for x in counts_list]
                
                # Find max group for text
                max_val = max(counts_list)
                max_idx = counts_list.index(max_val)
                top_group = DEFAULT_GROUPS[max_idx]
                pct = data_list[max_idx]
                
                text = f"מבוסס על {total} מקרים. הקבוצה הבולטת: {top_group} ({pct}%)."
            else:
                data_list = [0] * len(DEFAULT_GROUPS)
                text = "אין נתונים לחתך זה."
            
            final_output[city][offense] = {
                "data": data_list,
                "counts": counts_list,
                "total": total,
                "text": text
            }
            
    return final_output

def main():
    all_arrest_records = []
    total_indictments_global = 0
    global_meta = {'status_counts': {}, 'closing_counts': {}}
    
    # 1. Scan for files
    files = glob.glob(os.path.join(DATA_DIR, '*.xlsx'))
    print(f"Found {len(files)} Excel files.")
    
    for f in files:
        filename = os.path.basename(f)
        if filename.startswith('arrests'):
            records, ind_count = process_arrests(f)
            extra_stats = process_extra_sheets(f)
            
            all_arrest_records.extend(records)
            total_indictments_global += ind_count
            
            # Merge dictionary counts
            for key, val in extra_stats['status_counts'].items():
                global_meta['status_counts'][key] = global_meta['status_counts'].get(key, 0) + val
            for key, val in extra_stats['closing_counts'].items():
                global_meta['closing_counts'][key] = global_meta['closing_counts'].get(key, 0) + val
            
        # Here we can add elif filename.startswith('costs') ...
        
    print(f"Total arrest records processed: {len(all_arrest_records)}")
    print(f"Total indictments found: {total_indictments_global}")
    
    # 2. Aggregate
    final_json_data = aggregate_data(all_arrest_records)
    
    # Add the global indictment count directly to relevant sections or meta
    final_json_data['meta'] = {
        'total_indictments': total_indictments_global,
        'total_arrests': sum([r.get('weight', 1) for r in all_arrest_records]), # Sum weights
        'status_distribution': global_meta['status_counts'],
        'closing_reasons': global_meta['closing_counts']
    }

    # 3. International Comparison (2024)
    # Filter for 2024 records
    arrests_2024 = sum(r['weight'] for r in all_arrest_records if r.get('year') == 2024)
    israel_audience_2024 = 2000000
    israel_rate = (arrests_2024 / israel_audience_2024) * 100000 if israel_audience_2024 > 0 else 0
    
    final_json_data['comparison_stats'] = {
        'israel': {
            'rate': round(israel_rate, 2),
            'arrests': int(arrests_2024),
            'audience': israel_audience_2024,
            'flag': '🇮🇱',
            'label': 'ישראל'
        },
        'england': {
            'rate': 4.2,
            'flag': '🏴󠁧󠁢󠁥󠁮󠁧󠁿',
            'label': 'אנגליה'
        },
        'netherlands': {
            'rate': round((323 / 8000000) * 100000, 2),
            'flag': '🇳🇱',
            'label': 'הולנד',
            'arrests': 323,
            'audience': 8000000,
            'indictment_rate': 54
        },
        'spain': {
            'rate': round((90 / 15700000) * 100000, 2),
            'flag': '🇪🇸',
            'label': 'ספרד',
            'arrests': 90,
            'audience': 15700000,
            'admin_sanctions': 1675
        },
        'france': {
            'rate': round((613 / 12290125) * 100000, 2),
            'flag': '🇫🇷',
            'label': 'צרפת',
            'arrests': 613,
            'report_name': 'RAPPORT D’ACTIVITÉS N°3 – Instance Nationale du Supportérisme (INS)'
        }
    }


    # Process Indictment Stats (using the last file found - assuming single file for now or merge)
    # We need to process the file again or do it in the loop. 
    # Since we are outside the loop, we'll pick the first relevant file.
    target_file = files[0] # Simplification
    final_json_data['indictment_stats'] = process_indictment_stats(target_file)
    final_json_data['closing_stats'] = process_closing_reason_stats(target_file)
    
    # 4. Fines Analysis (Static Data Source: Reform Committee)
    final_json_data['fines_stats'] = {
        'chart_data': {
            'labels': ['2018/19', '2019/20', '2020/21', '2021/22'],
            'data': [2421710, 1730369, 1526166, 3501233]
        },
        'insights': {
            'total_fines': '9,179,478',
            'fans_share': 84,
            'lower_leagues_share': 51,
            'source': 'הוועדה לבחינת רפורמה בדרכי המאבק בהתפרעויות במשחקי הכדורגל בישראל'
        }
    }

    class NpEncoder(json.JSONEncoder):
        def default(self, obj):
            import numpy as np
            if isinstance(obj, (int, float)):
                if math.isnan(obj) or math.isinf(obj):
                    return None
                return obj
            if isinstance(obj, np.integer):
                return int(obj)
            if isinstance(obj, np.floating):
                if np.isnan(obj) or np.isinf(obj):
                    return None
                return float(obj)
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            return super(NpEncoder, self).default(obj)

    # 3. Export
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(final_json_data, f, ensure_ascii=False, indent=4, cls=NpEncoder)
        print(f"Successfully generated {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
