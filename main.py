from simulator import Simulator  # Simulator framework
from protocol.attendance_list import AttendanceListProcessor, Config, Failure  # protocol implementation


if __name__=="__main__":
    simulator = Simulator(Config.num_proc, AttendanceListProcessor, Failure)

    for i in range(50):
        print(f"cycle {i} begins")
        simulator.next_cycle()
