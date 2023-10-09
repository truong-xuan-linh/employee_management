import datetime
import pandas as pd
import pickle as pkl

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
    training_df = pd.read_sql_table('TapHuan', engine)
    result_df = pd.read_sql_table('KetQua', engine)

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
    for idx in range(staff_department_df.__len__()):
        absents = []
        total = staff_department_df.iloc[idx].counts
        department = staff_department_df.iloc[idx].BoPhan
        total_names = staff_department_df.iloc[idx].list_name.split(", ")
        total_ids = staff_department_df.iloc[idx].list_id.split(", ")
        
        training_info = training_department_df.loc[training_department_df["BoPhan"]==department]
        if not training_info.empty:
            training_info = training_info.iloc[0]
            num_done = training_info.counts
            num_names = training_info.list_name.split(", ")
            num_ids = training_info.list_id.split(", ")
            execution_time = training_info.last_time - start_time
        else:
            num_done = 0
            is_done = 0
            num_ids = []
            execution_time = current - start_time
        
        for id, name in zip(total_ids, total_names):
            if id not in num_ids:
                absents.append(f"{name} ({id})")
        
        training_result = result_df.loc[result_df["BoPhan"]==department]
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
            "execution_time": f"{execution_time.seconds // 60} phút, {execution_time.seconds % 60} giây"
        }
    
    return results