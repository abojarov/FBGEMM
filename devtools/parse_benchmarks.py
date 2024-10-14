BENCH_FOLDER="/home/abojarov/work/benchmarks/benchmark_32"

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

with open(f"{BENCH_FOLDER}/benchmarks_run_results.log") as file:
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


align_size = 15

fm_li = []
fs_li = []
bm_li = []
bs_li = []

for i, dl in enumerate(Data.data_list):
    fm_li.append([])
    fs_li.append([])
    bm_li.append([])
    bs_li.append([])
    md_str += f"\n\n## Data {i}: `{dl.current_branch}`\n\n"
    md_str += f"|{'id':^{align_size}}|{'alpha':^{align_size}}|{'output_t':^{align_size}}|{'emb_dim':^{align_size}}|{'bag_size':^{align_size}}|{'fwd_mean':^{align_size}}|{'fwd_stdev':^{align_size}}|{'bwd_mean':^{align_size}}|{'bwd_stdev':^{align_size}}|\n"
    md_str += f"|{'-'*align_size}|{'-'*align_size}|{'-'*align_size}|{'-'*align_size}|{'-'*align_size}|{'-'*align_size}|{'-'*align_size}|{'-'*align_size}|{'-'*align_size}|\n"
    for j, bdl in enumerate(dl.bench_data_list):
        # Normalize time to GB/s
        fw_norm_factor = 1.0e-3*bdl.param_dict['fwd_RW_megabytes']
        bw_norm_factor = 1.0e-3*bdl.param_dict['bwd_RW_megabytes']
        fs=statistics.stdev([fw_norm_factor/f for f in bdl.fwd_times_list])
        fm=statistics.mean([fw_norm_factor/f for f in bdl.fwd_times_list])
        bs=statistics.stdev([bw_norm_factor/b for b in bdl.bwd_times_list])
        bm=statistics.mean([bw_norm_factor/b for b in bdl.bwd_times_list])
        fwd_stdev=f"{fs:.6e}"
        fwd_mean=f"{fm:.6e}"
        bwd_stdev=f"{bs:.6e}"
        bwd_mean=f"{bm:.6e}"
        fm_li[-1].append(fm)
        fs_li[-1].append(fs)
        bm_li[-1].append(bm)
        bs_li[-1].append(bs)
        md_str += f"|{str((i,j)):>{align_size}}|{str(bdl.param_dict['alpha']):>{align_size}}|{str(bdl.param_dict['output_t']):>{align_size}}|{str(bdl.param_dict['emb_dim']):>{align_size}}|{str(bdl.param_dict['bag_size']):>{align_size}}|{fwd_mean:>{align_size}}|{fwd_stdev:>{align_size}}|{bwd_mean:>{align_size}}|{bwd_stdev:>{align_size}}|\n"


y0=[i for i in range(16)]
x0=fm_li[0]
xerr0=[2.0*fs for fs in fs_li[0]]

y1=[i for i in range(16)]
x1=fm_li[1]
xerr1=[2.0*fs for fs in fs_li[1]]

fig, (ax0) = plt.subplots(nrows=1, sharex=True)
fig.set_figwidth(10)
fig.set_figheight(10)
ax0.errorbar(x0, y0, xerr=xerr0, fmt='o', capsize=7, label=f"{Data.data_list[0].current_branch}")
ax0.errorbar(x1, y1, xerr=xerr1, fmt='o', capsize=7, label=f"{Data.data_list[1].current_branch}")
ax0.legend()
ax0.grid(which='minor', linestyle="--")
ax0.grid(which='major', linestyle="-")
ax0.set_title('Forward performance comparison')
ax0.set_ylabel('Second index from data table')
ax0.set_xlabel('RW speed [GB/s]')
ax0.set_yticks([2*i for i in range(8)])
ax0.set_yticks([2*i+1 for i in range(8)], minor=True)
plt.savefig(f"{BENCH_FOLDER}/image01.png", dpi=200)
plt.show()

md_str += "\n\n## Forward comparison\n\n"
md_str += "![img](./image01.png)\n"

with open(f"{BENCH_FOLDER}/output.md", "w") as text_file:
    text_file.write(md_str)   

pass
