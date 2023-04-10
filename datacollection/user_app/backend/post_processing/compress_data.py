import os
import shutil
import time

from datacollection.user_app.backend.constants import Post_Processing_Constants as ppc_const


class CompressDataService:
    # AB = 'ab'
    # DEPTH = 'depth'
    # DEPTH_AHAT = 'depth_ahat'
    # FRAMES = 'frames'
    # PV = 'pv'
    # ZIP = 'zip'

    def __init__(self, data_dir, depth_dir_name=ppc_const.DEPTH_AHAT, pv_dir_name=ppc_const.PHOTOVIDEO):
        self.data_dir = data_dir
        self.depth_root_dir = os.path.join(self.data_dir, depth_dir_name)
        self.pv_dir = os.path.join(self.data_dir, pv_dir_name)

    @classmethod
    def compress_dir(cls, base_dir_path, file_name, root_dir=None, compress_format=ppc_const.ZIP):
        file_count = len(os.listdir(base_dir_path))
        if root_dir is None:
            root_dir = base_dir_path
        file_path = os.path.join(root_dir, file_name)

        # ToDo: Add logs for the compression and file count instead of print statements
        print(f'Archiving {root_dir} - {file_name} ({file_count} files) STARTED')
        start_time = time.time()
        shutil.make_archive(file_path, compress_format, base_dir_path)
        end_time = time.time()
        print(f'Archiving {root_dir} - {file_name} ({file_count} files) FINISHED')
        print(f'Archive {file_path}.zip ({file_count} files) took {(end_time - start_time):.2f} seconds')

    @classmethod
    def delete_dir(cls, dir_path):
        print(f'Deleting directory {dir_path} STARTED')
        start_time = time.time()
        shutil.rmtree(dir_path)
        end_time = time.time()
        print(f'Deleting directory {dir_path} FINISHED')
        print(f'Deleting directory {dir_path} took {(end_time - start_time):.2f} seconds')

    def compress_depth(self):
        depth_dir = os.path.join(self.depth_root_dir, ppc_const.DEPTH)
        ab_dir = os.path.join(self.depth_root_dir, ppc_const.AB)
        self.compress_dir(depth_dir, ppc_const.DEPTH, self.depth_root_dir)
        self.compress_dir(ab_dir, ppc_const.AB, self.depth_root_dir)

    def compress_pv(self):
        frames_dir = os.path.join(self.pv_dir, ppc_const.FRAMES)
        self.compress_dir(frames_dir, ppc_const.FRAMES, self.pv_dir)

    def delete_depth_dir(self):
        depth_dir = os.path.join(self.depth_root_dir, ppc_const.DEPTH)
        ab_dir = os.path.join(self.depth_root_dir, ppc_const.AB)
        self.delete_dir(depth_dir)
        self.delete_dir(ab_dir)

    def delete_pv_dir(self):
        frames_dir = os.path.join(self.pv_dir, ppc_const.FRAMES)
        self.delete_dir(frames_dir)


if __name__ == '__main__':
    cds = CompressDataService(data_dir='../../../../../data/hololens/13_43')
    cds.compress_depth()
    cds.compress_pv()
