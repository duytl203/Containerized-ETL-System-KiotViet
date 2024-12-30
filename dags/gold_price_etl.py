from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import pandas as pd
import psycopg2, hashlib
from sqlalchemy import create_engine, text
import requests
from bs4 import BeautifulSoup

# Hàm lấy dữ liệu vàng
def get_table_gold_pnj():
    data = []
    try:
        response = requests.get('https://giavang.pnj.com.vn', timeout=10)  # Thêm timeout để tránh treo khi server không phản hồi
        
        response.raise_for_status()  # Gây lỗi nếu mã trạng thái không phải 2xx
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        headers = [th.text.strip() for th in soup.find_all("th", class_="style1")]
        table_body = soup.find_all("tbody")
        for tbody in table_body:

            rows = tbody.find_all("tr")        
            for row in rows:
                cells = row.find_all("td")
                if cells[0].get("rowspan"):
                    current_region = cells[0].text.strip()
                    data.append([current_region, cells[1].text.strip(), cells[2].text.strip(), cells[3].text.strip(), cells[4].text.strip()])
                else:
                    data.append([current_region, cells[0].text.strip(), cells[1].text.strip(), cells[2].text.strip(), cells[3].text.strip()])
        gold_table = pd.DataFrame(data, columns=headers)
        gold_table['Giá mua'] = gold_table['Giá mua'].astype(str).str.replace('.', '', regex=False).astype(int)
        gold_table['Giá bán'] = gold_table['Giá bán'].astype(str).str.replace('.', '', regex=False).astype(int)
        gold_table['Thời gian cập nhật'] = pd.to_datetime(gold_table['Thời gian cập nhật'], format="%d/%m/%Y %H:%M:%S")
        return gold_table
    except requests.exceptions.RequestException as e:
        print(f"Lỗi khi gửi yêu cầu HTTP: {e}")
    except Exception as e:
        print(f"Có lỗi xảy ra: {e}")

# Cấu hình kết nối PostgreSQL
db_url = 'postgresql+psycopg2://duytl:123456@192.168.56.1:5432/gia_vang'

# Tạo kết nối với PostgreSQL sử dụng SQLAlchemy
engine = create_engine(db_url)                                                                                          

# Hàm chèn hoặc cập nhật dữ liệu vào PostgreSQL
def insert_or_update(df):
    try:
        with engine.connect() as conn:
            for index, row in df.iterrows():
                insert_update_sql = """
                    INSERT INTO public.pnj_update (location, gold_type, price_buy, price_sale, last_updated)
                    VALUES (:location, :gold_type, :price_buy, :price_sale, :last_updated)
                    ON CONFLICT (location, gold_type, price_buy, price_sale, last_updated)
                    DO UPDATE 
                    SET location = EXCLUDED.location, 
                        gold_type = EXCLUDED.gold_type,
                        price_buy = EXCLUDED.price_buy,
                        price_sale = EXCLUDED.price_sale,
                        last_updated = EXCLUDED.last_updated;
                """              
                # Giá trị từ DataFrame
                values = {
                    "location": row['Khu vực'], 
                    "gold_type": row['Loại vàng'], 
                    "price_buy": row['Giá mua'], 
                    "price_sale": row['Giá bán'], 
                    "last_updated": row['Thời gian cập nhật']
                }
                
                # Thực thi câu lệnh
                conn.execute(text(insert_update_sql), values)
                print(f"Inserted/Updated record {index+1} with {row['Khu vực']},{row['Loại vàng']}, at {row['Thời gian cập nhật']}    ")
    except Exception as e:
        print(f"Error: {e}")

# Định nghĩa DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 12, 9),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'gold_price_etl',
    default_args=default_args,
    description='ETL Job to fetch and insert/update gold prices into PostgreSQL',
    schedule_interval='0 2 * * *',  # Chạy mỗi ngày lúc 9h sáng UTC
    catchup=False,
)

# Tạo task trong DAG
def etl_task():
    data = get_table_gold_pnj()
    if data is not None:
        insert_or_update(data)

def review_data():
    data = get_table_gold_pnj()
    if data is not None:
        # Chuyển đổi dữ liệu thành dạng chuỗi để hiển thị trong log
        print("Dữ liệu vàng mới nhất:")
        print(data.to_string(index=False))
    else:
        print("Không có dữ liệu để review.")

# Task review dữ liệu
review_task = PythonOperator(
    task_id='review_task',
    python_callable=review_data,
    dag=dag,
)

# Task ETL
etl_task = PythonOperator(
    task_id='etl_task',
    python_callable=etl_task,
    dag=dag,
)

# Thứ tự thực thi
review_task >> etl_task
