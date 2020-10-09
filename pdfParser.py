import PyPDF2
import camelot


vendor = 'jcrew'
pdf_filename = '馬克資料/19S06123+19S06124-0.430.2019.pdf'
pdf_file = open(pdf_filename, 'rb')
clothes_type = 'Top'

top_keys = {'BODY_FRONT': 'Front Body Length',
            'BODY_BACK': 'Back Body Length',
            'CHEST': 'Chest Circumference',
            'SWEEP': 'Sweep Circumference',
            'SLEEVE_LEN': 'CB Neck to Sleeve',
            'MUSCLE': 'Muscle Circumference',
            'CUFF_OPEN': 'Sleeve Opening Circumference',
            'CUFF_HEIGHT': 'Sleeve Cuff Heigh',
            'NECK_WIDTH': 'Neck Width at HPS',
            'COLLAR_HEIGHT': 'Collar Height at CB',
            'COLLAR_LEN': 'Collar Length'}


def get_key_values(keys, total_string_dictionary, key_paegs, base_size, key_start_index, key_record_string):
    output_keys = {}
    for key, values in keys.items():
        for i in range(len(key_paegs)):
            dfs = camelot.read_pdf(pdf_filename, pages=str(key_paegs[i] + 1))
            now_df = dfs[0].df
            # get start index
            start_index = now_df[now_df[0].str.contains(key_start_index) == True][0].index[0]
            new_df = now_df.loc[start_index + 1:, :]
            new_df.columns = [now_df.loc[start_index, :].values]

            # fix \n strings
            new_df = new_df.replace(r'\n',  ' ', regex=True)

            # compare key with csv
            row_index = None
            for index in new_df.index:
                row = new_df.loc[index, key_record_string].str.contains(values)
                if row[-1]:
                    row_index = index
                    break
            # print('row_index: {}'.format(row_index))
            if row_index != None:
                value = new_df.loc[row_index, base_size][-1]
                value = value.split(' ')
                if len(value) == 2:
                    value[-1] = float(value[-1].split('/')[0]) / float(value[-1].split('/')[1])
                    final_value = float(value[0]) + value[-1]
                else:
                    final_value = float(value[0])
                # print('value: {}'.format(final_value))
                output_keys[key] = final_value
                break
    return output_keys


def get_base_size(key_base_size, key_page_string):
    key_loc = key_page_string.find(key_base_size)
    # Base Size:XXXS, XXS, XS, S, M, L, XL, XXL, 2X, 3X
    base_size = key_page_string[key_loc + len(key_base_size) + 1: key_loc + len(key_base_size) + 5]
    base_size = base_size.replace(' ', '')
    return base_size


def get_key_page(key_page_name, total_string_dictionary):
    pages = []
    for page, string in total_string_dictionary.items():
        if key_page_name in string:
            pages.append(int(page))
    return pages


def main():
    total_string_dictionary = {}
    read_pdf = PyPDF2.PdfFileReader(pdf_file)
    number_of_pages = read_pdf.getNumPages()
    print('number of pages {}'.format(number_of_pages))
    # get type keys
    keys = {}
    key_start_index = ''
    key_page_name = ''
    key_base_size = ''
    key_record_string = ''
    if vendor == 'jcrew':
        key_start_index = 'Section POM #'
        key_page_name = 'Graded Measurement'
        key_base_size = 'Sample Size'
        key_record_string = 'POM Name'

    if clothes_type == 'Top':
        keys = top_keys

    # extract all string in pdf
    for i in range(number_of_pages):
        page = read_pdf.getPage(i)
        page_content = page.extractText()
        extrast_string = page_content.encode('utf-8')
        total_string_dictionary[i] = str(extrast_string)

    # get data pages
    key_paegs = get_key_page(key_page_name, total_string_dictionary)
    print('key_paegs: {}'.format(key_paegs))
    # print(total_string_dictionary[key_paegs[0]])

    # get Bas_ Size
    base_size = get_base_size(key_base_size, total_string_dictionary[key_paegs[0]])
    print('base_size: {}'.format(base_size))

    # use dataframe to get key values
    output_key_values = get_key_values(keys, total_string_dictionary, key_paegs, base_size, key_start_index,
                                       key_record_string)
    print(output_key_values)
    # now_df.to_csv('01_1.csv')


if __name__ == "__main__":
    main()
