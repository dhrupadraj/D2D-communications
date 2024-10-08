import numpy as np
import json
import matplotlib.pyplot as plt

def dBm_to_W(a):
    b=0.001*np.power(10,(a/10))
    return b

def W_to_dB(a):
    b = 10 * np.log10(a)
    return b

def dB_to_W(a):
    b = np.power(10, (a / 10))
    return b

def W_to_dBm(a):
    b = 10 * np.log10(a*1000)
    return b

def GeneratecellUEPosition(SimulationRegion,N_CU):
    global CU_Position_x
    global CU_Position_y
    CU_Position_x=np.random.uniform((-SimulationRegion/2),(SimulationRegion/2),N_CU)
    CU_Position_y=np.random.uniform((-SimulationRegion/2),(SimulationRegion/2),N_CU)
    print(CU_Position_x,CU_Position_y)

def GenerateD2DPosition(SimulationRegion,N_D2D):
    global D2D_Position_x
    global D2D_Position_y
    D2D_Position_x=np.random.uniform((-SimulationRegion/2),(SimulationRegion/2),N_D2D)
    D2D_Position_y=np.random.uniform((-SimulationRegion/2),(SimulationRegion/2),N_D2D)
    print(D2D_Position_x,D2D_Position_y)

def Distance(x,y):
    distpow=np.power(x,2)+np.power(y,2)
    Dist=np.sqrt(distpow)
    return Dist

def Pathloss(d,PLfactor):
    Loss=np.power(d,-PLfactor)
    return Loss

def cell_D2D_dis(x1,y1,x2,y2):
    x1m=np.tile(x1,(len(x2),1))
    y1m=np.tile(y1,(len(x2),1))
    x2m=np.tile(x2,(len(x1),1)).transpose()
    y2m=np.tile(y2,(len(x1),1)).transpose()
    dis=np.sqrt((x1m-x2m)**2+(y1m-y2m)**2)
    return dis

class Channel:
    def __init__(
            self,
            N_D2D=150,  #10,30,50,100,150
            N_CU=30,
            D2D_dis=30,
            SimulationRegion = 1000,
            AWGN=-174,
            W=10*10**6,
            PLfactor=4,
            PL_k=10**-2,
            CU_tr_Power=22,
            CU_min_SINR = 6,
            D2D_tr_Power_levels = 30,
            D2D_tr_Power_max = 23,
            D2D_min_SINR = 6,

    ):
        self.N_D2D= N_D2D
        self.N_CU=N_CU
        self.D2D_dis=D2D_dis
        self.SimulationRegion=SimulationRegion
        self.AWGN=AWGN
        self.W=W
        self.PLfactor=PLfactor
        self.PL_k=PL_k
        self.CU_tr_Power=CU_tr_Power
        self.CU_min_SINR=CU_min_SINR
        self.D2D_tr_Power_levels = D2D_tr_Power_levels
        self.D2D_tr_Power_max = D2D_tr_Power_max
        self.D2D_min_SINR=D2D_min_SINR
        self.collision_counter = 0
        self.collision_indicator = 0
        self.accessed_CUs = np.zeros(self.N_CU)
        self.power_levels = []
        self.CU_index = []

        self.action_space = np.array(range(0, self.D2D_tr_Power_levels*self.N_CU))   # 10 power levels * number of CU
        #self.action_space_true = np.transpose([np.tile(self.D2D_tr_Power_levels, self.N_CU), np.repeat(self.N_CU, len(self.D2D_tr_Power_levels))])
        #print(self.action_space_true)
        self.n_actions = len(self.action_space)

        GeneratecellUEPosition(self.SimulationRegion,self.N_CU)
        GenerateD2DPosition(self.SimulationRegion,self.N_D2D)

    def reset(self):

        # initialize power levels and construct action space
        self.power_levels = np.arange(1, float(self.D2D_tr_Power_levels + 1))
        for i in range(0, len(self.power_levels)):
            self.power_levels[i] = (self.D2D_tr_Power_max / self.D2D_tr_Power_levels) * self.power_levels[i]
        self.CU_index = np.arange(self.N_CU)
        self.action_space = self.action_space = np.transpose([np.tile(self.power_levels, len(self.CU_index)), np.repeat(self.CU_index, len(self.power_levels))])
        print(self.action_space)
        d_iB=Distance(CU_Position_x,CU_Position_y)
        CellUE_PL=Pathloss(d_iB,self.PLfactor)
        CellUE_ffading=np.random.exponential(1, size=self.N_CU)
        CellUE_sfading=np.random.lognormal(0, dB_to_W(8), size=self.N_CU)
        g_iB=self.PL_k*CellUE_PL*CellUE_ffading*CellUE_sfading
        D2D_Dis=self.D2D_dis
        D2D_PL=D2D_Dis**-self.PLfactor
        D2D_ffading=np.random.exponential(1, size=self.N_D2D)
        D2D_sfading=np.random.lognormal(0, dB_to_W(8), size=self.N_D2D)
        g_j=np.tile(self.PL_k*D2D_PL,(self.N_D2D))*D2D_ffading*D2D_sfading
        d_ij=cell_D2D_dis(CU_Position_x,CU_Position_y,D2D_Position_x,D2D_Position_y)
        G_ij_ffading=np.random.exponential(1, size=self.N_CU*self.N_D2D).reshape(self.N_D2D, self.N_CU)
        G_ij_sfading=np.random.lognormal(0, dB_to_W(8), size=self.N_CU*self.N_D2D).reshape(self.N_D2D, self.N_CU)
        G_ij=self.PL_k*d_ij**-self.PLfactor*G_ij_ffading*G_ij_sfading*10**-2   #### it's a matrix
        d_jB=Distance(D2D_Position_x,D2D_Position_y)
        g_jB_ffading=np.random.exponential(1, size=self.N_D2D)
        g_jB_sfading=np.random.lognormal(0, dB_to_W(8), size=self.N_D2D)
        g_jB=self.PL_k*d_jB**-self.PLfactor*g_jB_ffading*g_jB_sfading*10**-3
        g_jj_ffading = np.random.exponential(1, size=self.N_D2D)
        g_jj_sfading = np.random.lognormal(0, dB_to_W(8), size=self.N_D2D)
        d_J_j = np.zeros(self.N_D2D)
        g_J_j = np.zeros(self.N_D2D)
        G_j_j = np.zeros(shape=(self.N_D2D, self.N_D2D))
        for j in range(self.N_D2D):
            for j_ in range(self.N_D2D):
                d_J_j[j_] = np.sqrt((D2D_Position_x[j_]-D2D_Position_x[j])**2+(D2D_Position_y[j_]-D2D_Position_y[j])**2)   # size(d_jj) = (self.N_D2D) * 1   actually self.N_D2D-1
                if d_J_j[j_] == 0:
                    g_J_j[j_] = 0
                else:
                    g_J_j[j_] = self.PL_k*d_J_j[j_]**-self.PLfactor*g_jj_ffading[j_]*g_jj_sfading[j_]
            G_j_j[:, j] = g_J_j         # matrix
        return g_iB,g_j,G_ij,g_jB,G_j_j,d_ij

    def check_collisions(self, D2D_selected_CU):
        collision_flags = np.zeros(self.N_D2D)
        for i in range(self.N_CU):
            selected_by = np.where(D2D_selected_CU == i)[0]
            if len(selected_by) > 1:
                collision_flags[selected_by] = 1
        return collision_flags


    def CU_SINR_no_collision(self, g_iB, All_D2D_Power, g_jB, All_D2D_CU_index):
        self.accessed_CUs = np.zeros(self.N_CU)
        SINR_CU = np.zeros(self.N_CU)
        for i in range(self.N_CU):
            flag_0 = 0
            flag_1 = 0
            for j in range (self.N_D2D):
                if flag_0 == 1:
                    break
                for j_ in range(self.N_D2D):
                    if j != j_ and i == All_D2D_CU_index[j] == All_D2D_CU_index[j_]:  # if multiple D2Ds choose one and the same CU i
                        SINR_CU[i] = (dBm_to_W(self.CU_tr_Power) * g_iB[i]) / (dBm_to_W(self.AWGN))
                        flag_0 = 1
                        self.accessed_CUs[i] = 2
                        #print('collision occurs')
                        break
                else:
                    if i == All_D2D_CU_index[j]:   # define which D2D j choose CU i
                        SINR_CU[i] = (dBm_to_W(self.CU_tr_Power) * g_iB[i]) / (dBm_to_W(self.AWGN) + All_D2D_Power[j] * g_jB[j])
                        flag_1 = 1
                        self.accessed_CUs[i] = 1
                        #print('accessed')
                        break
                    else:
                        continue
            if flag_1 == 0 and flag_0 == 0:
                SINR_CU[i] = (dBm_to_W(self.CU_tr_Power) * g_iB[i]) / (dBm_to_W(self.AWGN))   # if no D2D chooses i
                self.accessed_CUs[i] = 0
        return SINR_CU

    def D2D_SINR_no_collision(self, All_D2D_Power, g_j, G_ij, G_j_j, All_D2D_CU_index, s):
        self.g_iJ = np.zeros(self.N_D2D)
        for j in range(self.N_D2D):
            self.g_iJ[j] = G_ij[j, int(All_D2D_CU_index[j])]      # for all D2D j choose CU i
        SINR_D2D= np.zeros(self.N_D2D)
        for j in range(self.N_D2D):
            for j_ in range(self.N_D2D):
                if j != j_ and All_D2D_CU_index[j] == All_D2D_CU_index[j_]:  # if collision occurs, SINR_D2D = 0
                    SINR_D2D[j] = 0
                    break
            else:
                SINR_D2D[j] = (All_D2D_Power[j] * g_j[j]) / (dBm_to_W(self.AWGN) + dBm_to_W(self.CU_tr_Power) * self.g_iJ[j])
        return SINR_D2D


    def state(self, SINR_CU):
        s = np.zeros(self.N_CU, dtype = np.float32)
        s = SINR_CU / 10**10
        return s



    def D2D_reward_no_collision(self, SINR_D2D, SINR_CU, All_D2D_CU_index, d_ij):
        r = np.zeros(self.N_D2D)
        D2D_r = np.zeros(self.N_D2D)
        CU_r = np.sum(self.W*np.log2(1 + SINR_CU))
        for j in range (self.N_D2D):
            for j_ in range(self.N_D2D):
                if j != j_ and All_D2D_CU_index[j] == All_D2D_CU_index[j_]:  # if multiple D2Ds choose the same CU, r = -0.2*(10**10) collision
                    self.collision_indicator += 1
                    D2D_r[j] = -0.2*(10**10)
                    r[j] = -0.2*(10**10)
                    #print('r collison')
                    break
            else:
                if SINR_CU[int(All_D2D_CU_index[j])] < dB_to_W(self.CU_min_SINR) or SINR_D2D[j] < dB_to_W(self.D2D_min_SINR):    # if the selection of the D2D j is ith CU which is under the threshold, r = -0.1*(10**10):
                    D2D_r[j] = -0.2*(10**10)
                    r[j] = -0.2*(10**10)
                    #print('r under threshold')
                else:
                    D2D_r[j] = self.W*np.log2(1 + SINR_D2D[j])
                    r[j] = D2D_r[j] + CU_r #- (d_ij[j][All_D2D_CU_index[j]] * (10**6))
        Net_r = sum(r)
        return r, Net_r, D2D_r, CU_r

if __name__ == "__main__":
    ch = Channel()
    ch.reset()
    print("Number of power levels:", len(ch.power_levels))
    print("CU indices:", ch.CU_index)

    # Simulate D2D selection of CUs
    D2D_selected_CU = np.random.choice(ch.CU_index, ch.N_D2D)
    collision_flags = ch.check_collisions(D2D_selected_CU)

    # Plotting the CU and D2D positions with collision indication
    plt.figure(figsize=(14, 7))

    # Plot CU Positions
    plt.subplot(1, 2, 1)
    plt.scatter(CU_Position_x, CU_Position_y, c='blue', marker='o', s=100, label='CU Positions')
    plt.title('Cellular User (CU) Positions')
    plt.xlabel('X Coordinate')
    plt.ylabel('Y Coordinate')
    plt.legend()

    # Plot D2D Positions with collision indication
    plt.subplot(1, 2, 2)
    plt.scatter(D2D_Position_x, D2D_Position_y, c='green', marker='x', s=100, label='D2D Positions')
    collisions = collision_flags == 1
    plt.scatter(D2D_Position_x[collisions], D2D_Position_y[collisions], c='red', marker='x', s=100, label='Colliding D2D Nodes')
    plt.scatter(D2D_Position_x[~collisions], D2D_Position_y[~collisions], c='green', marker='x', s=100, label='Non-Colliding D2D Nodes')
    plt.title('Device-to-Device (D2D) Positions and Collisions')
    plt.xlabel('X Coordinate')
    plt.ylabel('Y Coordinate')
    plt.legend()

    plt.tight_layout()
    plt.show()
