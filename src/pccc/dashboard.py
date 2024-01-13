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

    # Init dataframe
    staff_df = pd.read_sql_table('NhanVien', engine)
    training_df = pd.read_sql_table('DienTap', engine)
    result_df = pd.read_sql_table('KetQua', engine)
    staff_absent_df = pd.merge(staff_df, training_df["MaNV"], on='MaNV', how='left', indicator=True).query(
        "_merge == 'left_only'").drop('_merge', axis=1)
    # Process staff dataframe
    staff_department_df = staff_df.groupby(by=["BoPhan"]).agg({"Id": lambda x: len(x),
                                                               "HoTen": ", ".join,
                                                               "MaNV": ", ".join}).reset_index()
    staff_department_df = staff_department_df.rename(columns={
        "Id": "counts",
        "HoTen": "list_name",
        "MaNV": "list_id"
    })

    # Process training dataframe
    training_department_df = training_df.groupby(by=["BoPhan"]).agg({"Id": lambda x: len(x),
                                                                     "HoTen": ", ".join,
                                                                     "MaNV": ", ".join,
                                                                     "ThoiGian": "max"}).reset_index()
    training_department_df = training_department_df.rename(columns={
        "Id": "counts",
        "HoTen": "list_name",
        "MaNV": "list_id",
        "ThoiGian": "last_time"
    })

    # Get full dashboard results
    results = {}
    start_time = pkl.load(open(training_time_dir, "rb"))
    current = datetime.datetime.now()

    total_absent = 0
    total_staff = 0
    last_submit_time = start_time

    for idx in range(staff_department_df.__len__()):
        absents = []
        total = staff_department_df.iloc[idx].counts
        total_staff += total
        department = staff_department_df.iloc[idx].BoPhan
        total_names = staff_department_df.iloc[idx].list_name.split(", ")
        total_ids = staff_department_df.iloc[idx].list_id.split(", ")

        training_info = training_department_df.loc[training_department_df["BoPhan"] == department]
        if not training_info.empty:
            training_info = training_info.iloc[0]
            num_done = training_info.counts
            num_names = training_info.list_name.split(", ")
            num_ids = training_info.list_id.split(", ")
            execution_time = training_info.last_time - start_time
            last_submit_time = max(last_submit_time, training_info.last_time)
        else:
            num_done = 0
            is_done = 0
            num_ids = []
            execution_time = current - start_time

        for id, name in zip(total_ids, total_names):
            if id not in num_ids:
                absents.append(f"{name} ({id})")
                total_absent += 1

        training_result = result_df.loc[result_df["BoPhan"] == department]
        if not training_result.empty:
            is_done = training_result.iloc[0].HoanThanh
        else:
            is_done = 0

        if is_done:
            execution_time = training_result.iloc[0].ThoiGian - start_time

        results[department] = {
            "num_done": num_done,
            "total": total,
            "is_done": is_done,
            "absents": " ,".join(absents),
            "execution_time": f"{execution_time.seconds // 60} phút {execution_time.seconds % 60} giây",
            "last_time": training_info.last_time if not training_info.empty else None
        }

    # Calculate overall results
    complete_time = last_submit_time - start_time
    absent_percentage = 100 * total_absent / total_staff
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
        "CoMat": total_staff - total_absent,
        "VangMat": total_absent,
    }

    new_history_df = pd.DataFrame(new_history, index=[0])

    # Save to database
    new_history_df.to_sql('LichSu', engine, if_exists='append', index=False)

    return results, new_history, staff_absent_df