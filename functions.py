import pandas as pd
import re
from os import path


def depivot_data(data):
    # depends on parties being listed in all caps and metadata being listed with lowercase
    metadata_columns = [c for c in data.columns if not re.search(r'\b[A-Z]+\b', c)]
    data = pd.melt(data, id_vars=metadata_columns, var_name='Party')
    data.dropna(inplace=True)
    if '%' in data.loc[0, 'value']:
        data['value'] = data['value'].apply(lambda x: x.replace('%', ''))
    return data


def get_parties_and_percentages(text, dates):
    data = {}
    # Get party names present in projection
    parties = set(re.findall(r'\b[A-Z]{2,}\b', text))
    min_len = len(dates)
    # get data per party
    for party in parties:
        data[party] = re.findall(fr"{party}\s*(\d+%)", text) or ["0%"] * len(dates)
        min_len = min(min_len, len(data[party]))
    # Ensure same length for all lists
    for party in parties:
        data[party] = data[party][:min_len]
    # If GPC not present, add them
    green_tag = ''
    if 'OLP' in data or 'PCPO' in data:
        green_tag = green_tag + 'O'
    if 'LPC' in data or 'CPC' in data:
        green_tag = green_tag + 'C'
    if len(green_tag) != 1:
        raise Exception('Party list does not map to provincial or federal level')
    if f'GP{green_tag}' not in data:
        data[f'GP{green_tag}'] = ["0%"] * min_len
    return data


def extract_polling_data(soup_object, district):
    data = []
    for textbox in soup_object.find_all('div', id='daterangebutton_district-0'):
        # there should only be one of these
        text = textbox.get_text(strip=True)

        # Processing each item to extract useful data
        comma_index = text.find(',')
        if comma_index != -1:
            text = text[comma_index + 1:].strip()

        odds_index = re.search(r"(x?odds)", text, re.IGNORECASE)
        if odds_index:
            text = text[:odds_index.start()].strip()

        # Step 3.1 Adds a space to the right of %
        text = re.sub(r"(\d+%)", r"\1 ", text)

        # Step 3.2 Dates Clearing (yyyy-mm// ddx... to dd x...) and (yyyy-mm-dd [adds this space])
        text = re.sub(r"(\d{4}-\d{2}-\d{2})(?=\d{4}-\d{2}-\d{2})", r"\1 ", text)
        text = re.sub(r"(\d{4}-\d{2}-\d{2})(\S)", r"\1 \2", text)

        # Step 3.3 Clears any 8 number string into the last 4 numbers (starting date)
        text = re.sub(r"(\d{4})(\d{4})", r"\2", text)

        # print(f"Nearly Cleaned: {text}")

        # Step 3.4 Removes Date duplicates
        dates = re.findall(r"\d{4}-\d{2}-\d{2}", text)

        seen_dates = set()
        unique_dates = []
        for date in dates:
            if date not in seen_dates:
                unique_dates.append(date)
                seen_dates.add(date)

        date_iter = iter(unique_dates)
        text = re.sub(r"\d{4}-\d{2}-\d{2}", lambda match: unique_dates.pop(0) if unique_dates else "", text)

        # print(f"Final Cleaned Text: {text}")

        # Step 3.5 Dates (YYYY-MM-DD format)

        dates = re.findall(r"\d{4}-\d{2}-\d{2}", text)

        # Extracting dates and party percentages
        projection_data = get_parties_and_percentages(text, dates)

        # Step 6: Add metadata to dictionary
        for i in range(len(dates)):
            line_to_add = {}
            for p in projection_data:
                line_to_add[p] = projection_data[p][i]
            line_to_add.update({"District": district, "Date": dates[i]})
            data.append(line_to_add)
    return data


def clean_district_name(district_name):
    """Clean district names, ensuring consistent formatting."""
    replacements = {
        'Ã¢Â€Â”': ' ', 'Ã¢Â€Â‘': ' ', '—': ' ', '–': ' ', '-': ' ',
        '1000': 'Thousand', '&': 'and', '’': "'"
    }
    for old, new in replacements.items():
        district_name = district_name.replace(old, new)
    return re.sub(r"\s*\(.*\)$", "", district_name).strip()


def check_missing_districts(output_file, extracted_districts, df, all_districts):
    if path.exists(output_file):
        with open(output_file, 'r') as of:
            extracted_districts = set(df['District'].unique())
    missing_districts = set(all_districts) - extracted_districts
    print(f"Missing districts: {missing_districts}")