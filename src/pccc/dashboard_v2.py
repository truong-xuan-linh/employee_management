import pandas as pd
import pickle as pkl
import datetime


def get_results(engine, training_time_dir):
    """_summary_

    Args:
        engine (engine): engine from SQLAlchemy
        training_time_dir (String): training_time_dir from global variable

    Returns:
        Dictionary: result dictionary
    """
    start_time = pkl.load(open(training_time_dir, "rb"))
    current = datetime.datetime.now()
    
    # Init dataframe
    
    query=f"SELECT * FROM DiemDanh WHERE DATE(ThoiGian) == '{start_time.date()}'"
    
    staff_df = pd.read_sql(query, engine)
    training_df = pd.read_sql_table('DienTap2', engine)
    result_df = pd.read_sql_table('KetQua', engine)

    staff_department_df = staff_df.groupby(by=["BoPhan"]).agg({"Id": lambda x: len(x),
                                                               "ThoiGian": "max"
                                                               }).reset_index()
    staff_department_df = staff_department_df.rename(columns={
        "Id": "counts",
        "ThoiGian": "last_time"
    })
    
    # Get full dashboard results
    results = {}
    

    total_staff = 0
    last_submit_time = start_time
    total_done = 0
    for idx in range(staff_department_df.__len__()):
        total = staff_department_df.iloc[idx].counts
        total_staff += total
        department = staff_department_df.iloc[idx].BoPhan

        training_info = training_df.loc[training_df["BoPhan"] == department]
        if not training_info.empty:
            training_info = training_info.iloc[0]
            num_done = training_info.SoLuongCoMat
            total_done+=num_done
            execution_time = training_info.ThoiGian - start_time
            last_submit_time = max(last_submit_time, training_info.ThoiGian)
            is_done = 1
        else:
            num_done=0
            is_done = 0
            execution_time = current - start_time

        results[department] = {
            "num_done": num_done,
            "total": total,
            "is_done": is_done,
            "execution_time": f"{execution_time.seconds // 60} phút {execution_time.seconds % 60} giây",
            "last_time": start_time.strftime("%d/%m/%Y - %H:%M")
        }

    # Calculate overall results
    complete_time = last_submit_time - start_time
    absent_percentage = 100 * (total_staff - total_done) / (total_staff+1)
    present_percentage = 100 - absent_percentage
    if (complete_time.total_seconds() <= 5 * 60) and (present_percentage == 100):
        pass_fail = "Đạt yêu cầu về thời gian tập hợp không quá 5 phút và tỷ lệ có mặt 100%"
    elif ((complete_time.total_seconds() == 0 * 60) or (complete_time.total_seconds() > 5 * 60)) and (
            present_percentage != 100):
        pass_fail = "Không đạt yêu cầu về thời gian tập hợp không quá 5 phút và tỷ lệ có mặt 100%"
    elif (complete_time.total_seconds() > 5 * 60) and (present_percentage == 100):
        pass_fail = "Không đạt yêu cầu về thời gian tập hợp không quá 5 phút"
    elif (0 * 60 < complete_time.total_seconds() <= 5 * 60) and (present_percentage != 100):
        pass_fail = "Không đạt yêu cầu về tỷ lệ có mặt 100%"

    # Add to history
    new_history = {
        "MocThoiGian": start_time.strftime("%d/%m/%Y - %H:%M"),
        "KetQua": "Đạt" if pass_fail.startswith("Đạt") else "Không đạt",
        "LyDo": pass_fail,
        "ThoiGianHoanThanh": f"{complete_time.seconds // 60} phút {complete_time.seconds % 60} giây",
        "TongSo": total_staff,
        "CoMat": total_done,
        "VangMat": total_staff - total_done,
    }

    new_history_df = pd.DataFrame(new_history, index=[0])

    # Save to database
    new_history_df.to_sql('LichSu', engine, if_exists='append', index=False)

    return results, new_history