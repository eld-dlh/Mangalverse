import urllib.request

url = "https://pds-atmospheres.nmsu.edu/PDS/data/PDS4/Mars2020/mars2020_meda/data_calibrated_env/sol_0000_0089/sol_0001/WE__0001___________CAL_ATS_________________P01.CSV"
req = urllib.request.Request(url, headers={"User-Agent": "MarsExplorer/1.0"})

with urllib.request.urlopen(req, timeout=15) as resp:
    lines = [resp.readline().decode('utf-8', errors='ignore') for _ in range(5)]
    for l in lines:
        print(l.strip())
