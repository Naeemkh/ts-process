! Fortran code for computing response spectra.
! Originial version is writting by: Leonardo Ramirez-Guzman
! The code base is tailored for F2py.
!


subroutine max_osc_response(acc, npts, dt, period, csi, max_disp, &
    max_vel, max_acc)

    implicit none
    integer, intent(in) :: npts
    real, intent(in) :: acc(npts)
    real :: a(npts), v(npts), d(npts)
    real, intent(in) :: dt, period, csi 
    real, intent(out) :: max_disp, max_vel, max_acc
    integer :: i=1
    real, parameter :: PI = 3.14159265359
    real :: w, ww, csicsi, dcsiw, rcsi, csircs, wd, ueskdt, dcsiew, um2csi, e, &
     s, c0, ca, cb, cc, cd, cap, cbp, ccp, cdp 
    
    d(1) = 0.
    v(1) = 0.

    w = (2*PI)/period
    ww = w ** 2
    csicsi = csi ** 2
    dcsiw = 2. * csi * w

    rcsi = sqrt(1-csicsi)
    csircs = csi/rcsi
    wd = w * rcsi
    ueskdt = -1/(ww*dt)
    dcsiew = 2 * csi / w
    um2csi = (1.-2*csicsi)/wd
    e=exp(-w*dt*csi)
    s=sin(wd*dt)
    c0=cos(wd*dt)

    a(1) = -ww*d(1)-dcsiw*v(1) 

    ca = e * (csircs*s+c0)
    cb = e * s/wd
    cc = (e*((um2csi-csircs*dt)*s -(dcsiew+dt)*c0)+dcsiew)*ueskdt
    cd = (e*(-um2csi*s+dcsiew*c0)+dt-dcsiew)*ueskdt
    cap = -cb * ww
    cbp = e * (c0-csircs*s)
    ccp = (e*((w*dt/rcsi+csircs)*s+c0)-1.)*ueskdt
    cdp = (1.-ca)*ueskdt

    do i=2,npts
        d(i) = ca*d(i-1)+cb*v(i-1)+cc*acc(i-1)+cd*acc(i)
        v(i) = cap*d(i-1)+cbp*v(i-1)+ccp*acc(i-1)+cdp*acc(i)
        a(i) = -ww*d(i)-dcsiw*v(i)
    end do

    max_disp = 0
    max_vel = 0
    max_acc = 0

    do i=1,npts
        if (abs(a(i)) .gt. max_acc) then
            max_acc = abs(a(i))
        end if
    end do 

    do i=1,npts
        if (abs(v(i)) .gt. max_vel) then
            max_vel = abs(v(i))
        end if
    end do 

    do i=1,npts
        if (abs(d(i)) .gt. max_disp) then
            max_disp = abs(d(i))
        end if
    end do 

end subroutine max_osc_response


subroutine calc_response(acc, npts, dt, periods, n_prds,csi, max_disps, &
     max_vels, max_accs)
    implicit none
    integer, intent(in) :: npts, n_prds
    real, intent(in) :: acc(npts)
    real, intent(in) :: dt, csi
    real, intent(in) :: periods(n_prds) 
    real, intent(out) :: max_disps(n_prds), max_vels(n_prds), max_accs(n_prds)
    integer :: i=1

    do i=1,n_prds
        call max_osc_response(acc, npts, dt, periods(i), csi, max_disps(i),&
         max_vels(i), max_accs(i))
    end do

end subroutine calc_response
