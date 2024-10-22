def main(BENCH_FOLDER: str):

    def get_keystring_line(key: str, line: str) -> str:
        if key in line:
            return line[len(key):].strip()
        else:
            return ""

    class BenchData:
            
        def __init__(self):
            self.param_dict = dict()
            self.fwd_times_list = list()
            self.bwd_times_list  = list()


    class Data:

        data_list = []

        def __init__(self):
            self.folder_name = ""
            self.current_branch = ""
            self.commit_sha = ""
            self.bench_data_list = list()

        @staticmethod
        def append_data():
            Data.data_list.append(Data())
        
        @staticmethod
        def append_bench_data():
            Data.data_list[-1].bench_data_list.append(BenchData())

        @staticmethod
        def set_folder_name(fdname: str):
            Data.data_list[-1].folder_name = fdname

    with open(f"{BENCH_FOLDER}/bench_results.log") as file:
        count = 0
        while True:
            count += 1
            # Get next line from file
            line = file.readline()
            if not line:
                break
            valstr = get_keystring_line(">>>>>>> Call to run_benchmarks with :", line)
            if valstr:
                Data.append_data()
                Data.data_list[-1].folder_name = valstr.split('/')[-2]
            valstr = get_keystring_line(">>>>>>> Current HEAD       :", line)
            if valstr:
                Data.data_list[-1].current_branch = valstr
            valstr = get_keystring_line(">>>>>>> Current commit SHA :", line)
            if valstr:
                Data.data_list[-1].commit_sha = valstr
            valstr = get_keystring_line(">>>>>>> Parameters set:", line)
            if valstr:
                Data.append_bench_data()
                for param in valstr.replace(' ','').split(','):
                    if param.split('=')[0] == "alpha":
                        Data.data_list[-1].bench_data_list[-1].param_dict[param.split('=')[0]] = float(param.split('=')[1])
                    elif param.split('=')[0] == "output_t":
                        Data.data_list[-1].bench_data_list[-1].param_dict[param.split('=')[0]] = param.split('=')[1]
                    else:
                        Data.data_list[-1].bench_data_list[-1].param_dict[param.split('=')[0]] = int(param.split('=')[1])
            valstr = get_keystring_line("INFO:root:Managed option:", line)
            if valstr:
                Data.data_list[-1].bench_data_list[-1].param_dict['managed_option'] = valstr
            valstr = get_keystring_line("INFO:root:Embedding parameters:", line)
            if valstr:
                Data.data_list[-1].bench_data_list[-1].param_dict['emb_gparams'] = float(valstr.split(' ')[0])
                Data.data_list[-1].bench_data_list[-1].param_dict['emb_gbytes'] = float(valstr.split(' ')[3])
            valstr = get_keystring_line("INFO:root:Accessed weights per batch:", line)
            if valstr:
                Data.data_list[-1].bench_data_list[-1].param_dict['access_weights_gbytes'] = float(valstr.split(' ')[0])
            valstr = get_keystring_line("INFO:root:Forward,", line)
            if valstr:
                valstr = valstr.replace("  ", ' ')
                Data.data_list[-1].bench_data_list[-1].param_dict['fwd_B'] = int(valstr.split(' ')[1][:-1])
                Data.data_list[-1].bench_data_list[-1].param_dict['fwd_E'] = int(valstr.split(' ')[3][:-1])
                Data.data_list[-1].bench_data_list[-1].param_dict['fwd_T'] = int(valstr.split(' ')[5][:-1])
                Data.data_list[-1].bench_data_list[-1].param_dict['fwd_D'] = int(valstr.split(' ')[7][:-1])
                Data.data_list[-1].bench_data_list[-1].param_dict['fwd_L'] = int(valstr.split(' ')[9][:-1])
                Data.data_list[-1].bench_data_list[-1].param_dict['fwd_W'] = False if valstr.split(' ')[11][:-1] == 'False' else True
                Data.data_list[-1].bench_data_list[-1].param_dict['fwd_RW_megabytes'] = float(valstr.split(' ')[13])
                Data.data_list[-1].bench_data_list[-1].param_dict['fwd_BW_gb_sec'] = float(valstr.split(' ')[16])
                Data.data_list[-1].bench_data_list[-1].param_dict['fwd_T_us'] = float(valstr.split(' ')[19][:-2])
            valstr = get_keystring_line("INFO:root:Forward times:", line)
            if valstr:
                Data.data_list[-1].bench_data_list[-1].fwd_times_list = eval(valstr)
            valstr = get_keystring_line("INFO:root:Backward,", line)
            if valstr:
                valstr = valstr.replace("  ", ' ')
                Data.data_list[-1].bench_data_list[-1].param_dict['bwd_B'] = int(valstr.split(' ')[1][:-1])
                Data.data_list[-1].bench_data_list[-1].param_dict['bwd_E'] = int(valstr.split(' ')[3][:-1])
                Data.data_list[-1].bench_data_list[-1].param_dict['bwd_T'] = int(valstr.split(' ')[5][:-1])
                Data.data_list[-1].bench_data_list[-1].param_dict['bwd_D'] = int(valstr.split(' ')[7][:-1])
                Data.data_list[-1].bench_data_list[-1].param_dict['bwd_L'] = int(valstr.split(' ')[9][:-1])
                Data.data_list[-1].bench_data_list[-1].param_dict['bwd_RW_megabytes'] = float(valstr.split(' ')[11])
                Data.data_list[-1].bench_data_list[-1].param_dict['bwd_BW_gb_sec'] = float(valstr.split(' ')[14])
                Data.data_list[-1].bench_data_list[-1].param_dict['bwd_T_us'] = float(valstr.split(' ')[17][:-2])
            valstr = get_keystring_line("INFO:root:Backward times:", line)
            if valstr:
                Data.data_list[-1].bench_data_list[-1].bwd_times_list = eval(valstr)


    import matplotlib.pyplot as plt
    import statistics
    import numpy as np

    md_str = f"""# Benchmark results comparison

    We compare results for two different commits:

    1. Branch HEAD name `{Data.data_list[0].current_branch}` from folder `{Data.data_list[0].folder_name}`.
    The commit SHA is `{Data.data_list[0].commit_sha}`.

    2. Branch HEAD name `{Data.data_list[1].current_branch}` from folder `{Data.data_list[1].folder_name}`.
    The commit SHA is `{Data.data_list[1].commit_sha}`.

    """


    align_size = 18

    fm_li = []
    fs_li = []
    bm_li = []
    bs_li = []
    fs_percent_li = []
    fm_percent_li = []
    bs_percent_li = []
    bm_percent_li = []

    for i, dl in enumerate(Data.data_list):
        fm_li.append([])
        fs_li.append([])
        bm_li.append([])
        bs_li.append([])
        md_str += f"\n\n## Data {i}: `{dl.current_branch}`\n\n"
        if i == 1:
            fm_percent_li.append([])
            fs_percent_li.append([])
            bm_percent_li.append([])
            bs_percent_li.append([])
            md_str += f"|{'id':^{align_size}}|{'alpha':^{align_size}}|{'output_t':^{align_size}}|{'emb_dim':^{align_size}}|{'bag_size':^{align_size}}|{'fwd_mean':^{align_size}}|{'fwd_stdev':^{align_size}}|{'bwd_mean':^{align_size}}|{'bwd_stdev':^{align_size}}|{'fwd_mean_percent':^{align_size}}|{'fwd_stdev_percent':^{align_size}}|{'bwd_mean_percent':^{align_size}}|{'bwd_stdev_percent':^{align_size}}|\n"
            md_str += f"|{'-'*align_size}|{'-'*align_size}|{'-'*align_size}|{'-'*align_size}|{'-'*align_size}|{'-'*align_size}|{'-'*align_size}|{'-'*align_size}|{'-'*align_size}|{'-'*align_size}|{'-'*align_size}|{'-'*align_size}|{'-'*align_size}|\n"
        else:
            md_str += f"|{'id':^{align_size}}|{'alpha':^{align_size}}|{'output_t':^{align_size}}|{'emb_dim':^{align_size}}|{'bag_size':^{align_size}}|{'fwd_mean':^{align_size}}|{'fwd_stdev':^{align_size}}|{'bwd_mean':^{align_size}}|{'bwd_stdev':^{align_size}}|\n"
            md_str += f"|{'-'*align_size}|{'-'*align_size}|{'-'*align_size}|{'-'*align_size}|{'-'*align_size}|{'-'*align_size}|{'-'*align_size}|{'-'*align_size}|{'-'*align_size}|\n"
        for j, bdl in enumerate(dl.bench_data_list):
            # Normalize time to GB/s
            fw_norm_factor = 1.0e-3*bdl.param_dict['fwd_RW_megabytes']
            bw_norm_factor = 1.0e-3*bdl.param_dict['bwd_RW_megabytes']
            freqli = [fw_norm_factor/f for f in bdl.fwd_times_list]
            fs=statistics.stdev(freqli)
            fm=statistics.mean(freqli)
            freqli = [bw_norm_factor/f for f in bdl.bwd_times_list]
            bs=statistics.stdev(freqli)
            bm=statistics.mean(freqli)
            fwd_stdev=f"{fs:.6e}"
            fwd_mean=f"{fm:.6e}"
            bwd_stdev=f"{bs:.6e}"
            bwd_mean=f"{bm:.6e}"
            fm_li[-1].append(fm)
            fs_li[-1].append(fs)
            bm_li[-1].append(bm)
            bs_li[-1].append(bs)
            if i == 1:
                freqli = [fw_norm_factor/f for f in bdl.fwd_times_list]
                fs_percent = statistics.stdev([100.0*((f - fm_li[0][j])/fm_li[0][j]) for f in freqli])
                fm_percent = statistics.mean([100.0*((f - fm_li[0][j])/fm_li[0][j]) for f in freqli])
                freqli = [bw_norm_factor/f for f in bdl.bwd_times_list]
                bs_percent = statistics.stdev([100.0*((f - bm_li[0][j])/bm_li[0][j]) for f in freqli])
                bm_percent = statistics.mean([100.0*((f - bm_li[0][j])/bm_li[0][j]) for f in freqli])
                fwd_stdev_percent=f"{fs_percent:2.3f}"
                fwd_mean_percent=f"{fm_percent:2.3f}"
                bwd_stdev_percent=f"{bs_percent:2.3f}"
                bwd_mean_percent=f"{bm_percent:2.3f}"
                fm_percent_li[-1].append(fm_percent)
                fs_percent_li[-1].append(fs_percent)
                bm_percent_li[-1].append(bm_percent)
                bs_percent_li[-1].append(bs_percent)
                md_str += f"|{str((i,j)):>{align_size}}|{str(bdl.param_dict['alpha']):>{align_size}}|{str(bdl.param_dict['output_t']):>{align_size}}|{str(bdl.param_dict['emb_dim']):>{align_size}}|{str(bdl.param_dict['bag_size']):>{align_size}}|{fwd_mean:>{align_size}}|{fwd_stdev:>{align_size}}|{bwd_mean:>{align_size}}|{bwd_stdev:>{align_size}}|{fwd_mean_percent:>{align_size}}|{fwd_stdev_percent:>{align_size}}|{bwd_mean_percent:>{align_size}}|{bwd_stdev_percent:>{align_size}}|\n"
            else:
                md_str += f"|{str((i,j)):>{align_size}}|{str(bdl.param_dict['alpha']):>{align_size}}|{str(bdl.param_dict['output_t']):>{align_size}}|{str(bdl.param_dict['emb_dim']):>{align_size}}|{str(bdl.param_dict['bag_size']):>{align_size}}|{fwd_mean:>{align_size}}|{fwd_stdev:>{align_size}}|{bwd_mean:>{align_size}}|{bwd_stdev:>{align_size}}|\n"

    def plot_data(std_li, mean_li, title, image_file_name, percent=False):
        y0=[i for i in range(16)]
        x0=mean_li[0]
        xerr0=[2.0*fs for fs in std_li[0]]

        if not percent:
            y1=[i for i in range(16)]
            x1=mean_li[1]
            xerr1=[2.0*fs for fs in std_li[1]]

        fig, (ax0) = plt.subplots(nrows=1, sharex=True)
        fig.set_figwidth(15)
        fig.set_figheight(10)
        ax0.errorbar(x0, y0, xerr=xerr0, fmt='o', capsize=7, label=f"{Data.data_list[0].current_branch}")
        if not percent:
            ax0.errorbar(x1, y1, xerr=xerr1, fmt='o', capsize=7, label=f"{Data.data_list[1].current_branch}")
        ax0.legend()
        ax0.grid(which='minor', linestyle="--")
        ax0.grid(which='major', linestyle="-")
        ax0.set_title(title)
        ax0.set_ylabel('Second index from data table')
        if not percent:
            ax0.set_xlabel('RW speed [GB/s]')
        else:
            ax0.set_xlabel('Speed increase [%]')
        ax0.set_yticks([2*i for i in range(8)])
        ax0.set_yticks([2*i+1 for i in range(8)], minor=True)
        plt.savefig(f"{BENCH_FOLDER}/{image_file_name}", dpi=200)
        plt.show()
        
    plot_data(fs_li, fm_li, "Forward performance comparison", "image01.png")
    md_str += f"\n\n## Forward performance comparison\n\n"
    md_str += f"![img](./image01.png)\n"

    plot_data(bs_li, bm_li, "Backward performance comparison", "image02.png")
    md_str += f"\n\n## Backward performance comparison\n\n"
    md_str += f"![img](./image02.png)\n"

    plot_data(fs_percent_li, fm_percent_li, "Forward speed increase", "image03.png", percent=True)
    md_str += f"\n\n## Forward speed increase\n\n"
    md_str += f"![img](./image03.png)\n"

    plot_data(bs_percent_li, bm_percent_li, "Backward speed increase", "image04.png", percent=True)
    md_str += f"\n\n## Backward speed increase\n\n"
    md_str += f"![img](./image04.png)\n"

    with open(f"{BENCH_FOLDER}/output.md", "w") as text_file:
        text_file.write(md_str)   


if __name__ == "__main__":
    import sys
    from pathlib import Path
    home = Path.home()
    BENCH_FOLDER=f"{home}/work/benchmarks/benchmark_03"
    if len(sys.argv) > 1:
        BENCH_FOLDER=sys.argv[1]
    print(f"Running parse_benchmarks with folder `{BENCH_FOLDER}`")
    main(BENCH_FOLDER=BENCH_FOLDER)