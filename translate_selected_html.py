import pandas as pd
import os
import re
import sys

# 엑셀에서 "KOR" → "CHN" 매핑 불러오기
def load_translation_map(excel_file):
    df = pd.read_excel(excel_file)
    df = df[['KOR', 'CHN']].dropna()

    translation_map = {}
    for i, row in df.iterrows():
        kor = str(row['KOR']).strip()
        chn = str(row['CHN']).strip()
        if kor:
            translation_map[kor] = chn
    return translation_map

def normalize_text(text):
    text = re.sub(r'<br\s*/?>|<\/?p>', ' ', text)  # <br>, <br/>, <p>, </p> 등을 공백으로 대체
    
    text = ' '.join(text.split())
    
    # 따옴표 정규화
    text = text.replace('"', '"').replace('"', '"')
    
    return text

def translate_file(file_path, translation_map):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    translated = set()
    not_translated = set()

    # 번역 항목을 길이 기준으로 정렬 (긴 것부터 처리)
    sorted_translations = sorted(translation_map.items(), key=lambda x: len(x[0]), reverse=True)

    for kor, chn in sorted_translations:
        # 원본 텍스트로 먼저 시도
        if kor in content:
            content = content.replace(kor, chn)
            translated.add(kor)
            continue
            
        # HTML 태그를 고려한 정규화된 텍스트로 시도
        kor_clean = normalize_text(kor)
        content_clean = normalize_text(content)
        
        if kor_clean in content_clean:
            # 원본 텍스트에서 해당 부분을 찾아 교체
            # HTML 태그를 보존하면서 텍스트만 교체하기 위한 패턴
            pattern = re.escape(kor).replace(r'\ ', r'\s*(?:<br\s*/?>\s*)?')
            content = re.sub(pattern, chn, content)
            translated.add(kor)
        else:
            not_translated.add(kor)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"처리 완료: {os.path.basename(file_path)}")
    if not_translated:
        print("\n번역되지 않은 텍스트:")
        for text in not_translated:
            print(f"- {text}")

# 메인 실행 로직
def main():
    if len(sys.argv) < 2:
        print("사용법: python translate_selected_html.py file1.html file2.html ...")
        return

    base_path = './chn/esg/social'
    excel_file = 'lgd_esg_translate.xlsx'
    translation_map = load_translation_map(excel_file)

    for file_name in sys.argv[1:]:
        full_path = os.path.join(base_path, file_name)
        if os.path.exists(full_path):
            translate_file(full_path, translation_map)
        else:
            print(f"파일 없음: {file_name}")

if __name__ == "__main__":
    main()
