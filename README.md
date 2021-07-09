# Finnish apartment sales and turnover rate

## Usage

```
python3.9 -m pip install -r requirements.txt
python3.9 main.py sales.db
sqlite3 sales.db 'select min(turnover), max(turnover), avg(turnover) from apartment_sales;'
```
