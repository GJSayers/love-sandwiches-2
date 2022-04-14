import gspread
from google.oauth2.service_account import Credentials

SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
    ]

CREDS = Credentials.from_service_account_file('creds.json')
SCOPED_CREDS = CREDS.with_scopes(SCOPE)
GSPREAD_CLIENT = gspread.authorize(SCOPED_CREDS)
SHEET = GSPREAD_CLIENT.open('love_sandwiches')


def get_sales_data():
    """
    Get sales data input from the user.
    Run a while loop to collect valid data from user,
    continually requesting until valid data is submitted.
    """
    while True:
        print("Please enter sales data from the last market")
        print("Data should be 6 numbers separated by commas")
        print("Example: 10,10,35,45,52,62\n")

        data_str = input("Enter your data here:\n")

        sales_data = data_str.split(",")
        validate_data(sales_data)
        if validate_data(sales_data):
            print("Data is valid!")
            break
    return sales_data


def validate_data(values):
    """ 
    Inside the try, converts string values to int.
    Raises ValueError is strings cannot be converted to int, 
    or if there are not exactly 6 values
    """
    try:
        [int(value) for value in values]
        if len(values) != 6:
            raise ValueError(
                f"Exactly 6 values required, you provided {len(values)}"
            )
    except ValueError as e:
        print(f"Invalid data: {e}, please try again.\n")
        return False

    return True


# def update_sales_worksheet(data):
#     """
#     Update sales worksheet, add new row with the list data provided
#     """
#     print("Updating sales worksheet...\n")
#     sales_worksheet = SHEET.worksheet("sales")
#     sales_worksheet.append_row(data)
#     print("Sales worksheet updated successfully. \n")




# def update_surplus_worksheet(data):
#     """
#     Update suplus worksheet, add new row with the list data provided
#     """
#     print("Updating surplus worksheet...\n")
#     surplus_worksheet = SHEET.worksheet("surplus")
#     surplus_worksheet.append_row(data)
#     print("Surplus worksheet updated successfully. \n")


def update_worksheet(data, worksheet):
    """
    Refactored functionUpdates both the sales and the 
    surplus worksheets with their respective data
    """
    print(f"Updating {worksheet} worksheet...\n")
    worksheet_to_update = SHEET.worksheet(worksheet)
    worksheet_to_update.append_row(data)
    print(f"{worksheet} worksheet updated successfully. \n")


def calculate_surplus_data(sales_row):
    """
    Compare sales data against stock values to calculate surplus data.
    Positive surplus indicates wasted product
    Negative surplus data indicates extra made to order / original stock sold
    """
    print("Calculating surplus data...\n")
    stock = SHEET.worksheet("stock").get_all_values()
    stock_row = stock[-1]
    surplus_data = []
    for stock, sales in zip(stock_row, sales_row):
        surplus = int(stock) - int(sales)
        surplus_data.append(surplus)

    return surplus_data

def get_last_5_sales_days():
    """
    retreive the last 5 days sales data to predict stock needed
    """
    sales = SHEET.worksheet("sales")
    # row and column indexing starts at 1 not zero
    columns = []
    # range cannot be 6 because the first ind would be 0 and this does not tie in with the 1-based indexing on the sheet.
    for ind in range(1, 7):
        column = sales.col_values(ind)
        columns.append(column[-5:])
    return columns

def calculate_stock_data(data):
    """
    Calculate the average stock data for each 
    """
    print("calculating stock data...\n")
    new_stock_data = []

    for column in data:
        int_column = [int(num) for num in column]
        average = sum(int_column) / len(int_column)
        stock_num = average * 1.1
        new_stock_data.append(round(stock_num))
    return new_stock_data


def get_stock_values(data):
    """
    Make a dictionary of the headings and the stock values to print
    stock needed for the next day
    """
    headings = SHEET.worksheet("stock").row_values(1)
    stock_dict = dict(zip(headings, data))
    print(stock_dict)
    return stock_dict


def main():
    """
    Run all programme fuctions
    """
    data = get_sales_data()
    sales_data = [int(num) for num in data]
    update_worksheet(sales_data, "sales")
    new_surplus_data = calculate_surplus_data(sales_data)
    update_worksheet(new_surplus_data, "surplus")
    sales_columns = get_last_5_sales_days()
    stock_data = calculate_stock_data(sales_columns)
    update_worksheet(stock_data, "stock")
    get_stock_values(data)


print("Welcome to love sandwiches Data Automation")
main()


