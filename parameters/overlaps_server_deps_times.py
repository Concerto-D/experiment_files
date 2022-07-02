import json

if __name__ == "__main__":
    output = json.load(open("generations/2022-07-01_17-17-43/uptimes-60-30-12-0_5-0_6.json"))

    # for i in range(len(output[0])):
    #     print(f"FREQ: {i} ------------------")
    #     for j in range(len(output)):
    #         print(output[j][i], end="")
    #     print("-----------------")
    print("experiment_files/parameters/uptimes/uptimes-60-30-12-0_2-0_3.json")
    for i in range(len(output[0])):
        print(f"--- FREQ: {i} -----")
        for k in range(1, len(output)):
            o0, d0 = output[0][i]
            o2, d2 = output[k][i]
            print(output[0][i], end="")
            print(output[k][i], end="")
            print(f"   Server/dep{k-1}   Overlap: {max(min(o0+d0, o2+d2) - max(o0, o2), 0)}")
        print("-----------------\n")