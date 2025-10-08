from get_schedule import get_schedule
from make_table import make_table

def main():
    schedule = get_schedule(from_file=False)
    if schedule is None:
        return
    print("由Tibame取得最新課表")
    make_table(schedule)
    
if __name__ == "__main__":
    main()
