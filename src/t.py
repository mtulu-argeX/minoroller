A="states: pitch:0;roll:0;yaw:0;vgx:0;vgy:0;vgz:0;templ:85;temph:86;tof:10;h:0;bat:8;baro:796.24;time:0;agx:-4.00;agy:0.00;agz:-998.00;"
A=[float(x.split(":")[1]) for x in A.strip().split(" ")[1].split(";")[:-1]]
print ("%4.0f %4.0f %4.0f %4.0f %4.0f %4.0f %4.0f %4.0f %4.0f" % (A[0], A[1], A[2],  A[3], A[4], A[5],A[9], A[10], A[12] ))
