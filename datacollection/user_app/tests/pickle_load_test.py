import pickle


def verify_pickle(file_name):
    file = open(file_name, 'rb')
    object_file = pickle.load(file)
    file.close()
    print("Loaded pickle file: ", file_name)
    print("Type of object: ", type(object_file))
    print("Length of object: ", len(object_file))
    print()
    return object_file


if __name__ == '__main__':
    recording_id = "22_37"

    pv_pose_file_name = f"/home/ptg/CODE/data/hololens/{recording_id}/pv/{recording_id}_pv_pose.pkl"
    verify_pickle(pv_pose_file_name)

    depth_pose_file_name = f"/home/ptg/CODE/data/hololens/{recording_id}/depth_ahat/{recording_id}_depth_ahat_pose.pkl"
    verify_pickle(depth_pose_file_name)

