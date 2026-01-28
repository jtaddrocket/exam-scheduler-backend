from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from .models import *

def makematrix(subs, tot_sub, subid):
    # Making the adj. matrix
    mat=[[0 for i in range(tot_sub)]for i in range(tot_sub)]
    for sub in subs:
        l=len(sub)        
        for i in range(l):
            for j in range(i+1,l):
                a,b = subid[sub[i]['id']] , subid[sub[j]['id']]
                mat[a][b], mat[b][a] = 1,1

    for m in mat:
        print(*m) 
    return mat


def timetable(mat):
    # MAIN BACKTRACKING ALGORITHM
    l = len(mat)
    ans = [0]*l
    k=0
    color = 1
    while k>=0 :
        for i in range(l):
            if mat[k][i]==1:
                if ans[i]==color:
                    color+=1
                    continue
        ans[k]=color
        print(ans)
        color=1
        k+=1
        if k==l:
            break;

    return ans


def start(request):
    if not request.user.is_authenticated:
        return redirect('/login/')
    
    not_admin=False
    all_subjects = Subject.objects.values()
    reg_subjects = []
    uid = 'admin123'
    if request.user.username!='admin':
        not_admin=True
        # Tự động tạo Mapping nếu chưa có
        mapping, created = Mapping.objects.get_or_create(
            user=request.user,
            defaults={'uid': request.user.id}
        )
        reg_subjects = mapping.sub.values()
        uid = mapping
    regno = len(reg_subjects)

    aval_subjects=[]
    for sub in all_subjects:
        if sub not in reg_subjects:
            aval_subjects.append(sub)
            
    prms = {'regno':regno,'uid':uid, 'all_sub':aval_subjects,'reg_sub':reg_subjects,'is_admin':not not_admin}
    return render(request, 'start.html', prms)


def generate(request):
    if not request.user.is_authenticated :
        return redirect('/login/')

    if request.user.username != 'admin':
        return redirect('/')

    mappings = Mapping.objects.all()
    subjects = Subject.objects.values()

    counter = 0
    subid = dict()  #to prevent error after deletion of subjects
    for subj in subjects:
        subid[subj['id']]=counter
        counter+=1
    
    tot_sub = subjects.count()
    subs=[]
    for mapping in mappings:
        subs.append(list(mapping.sub.values()))

    mat = makematrix(subs, tot_sub, subid)
    ans = timetable(mat)
    res=[[] for i in range(len(set(ans)))]

    mcount=0
    for i in range(1,max(ans)+1):
        mcount = max(mcount,ans.count(i))
    
    for subject in subjects:
        i=subid[subject['id']]
        res[ans[i]-1].append(subject['name'])

    for i in range(len(res)):
        for j in range(mcount-len(res[i])):
            res[i].append('-')

    return render(request, 'table.html',{'res':res})


def view_registrations(request):
    """Trang admin xem danh sách môn học mà sinh viên đã đăng ký"""
    if not request.user.is_authenticated:
        return redirect('/login/')

    if request.user.username != 'admin':
        return redirect('/')

    # Lấy tất cả mappings với thông tin user và subjects
    mappings = Mapping.objects.all().select_related('user').prefetch_related('sub')
    
    # Tạo danh sách sinh viên và môn học đã đăng ký
    student_registrations = []
    for mapping in mappings:
        subjects = mapping.sub.all()
        student_registrations.append({
            'user': mapping.user,
            'username': mapping.user.username,
            'email': mapping.user.email or '(không có)',
            'uid': mapping.uid,
            'subjects': subjects,
            'subject_count': subjects.count(),
            'subject_names': [s.name for s in subjects]
        })
    
    # Sắp xếp theo số môn đăng ký giảm dần
    student_registrations.sort(key=lambda x: x['subject_count'], reverse=True)
    
    # Tổng số sinh viên đã đăng ký
    total_students = len(student_registrations)
    
    # Tổng số môn học đã được đăng ký
    all_subjects = Subject.objects.all()
    total_subjects = all_subjects.count()
    
    context = {
        'student_registrations': student_registrations,
        'total_students': total_students,
        'total_subjects': total_subjects,
    }
    
    return render(request, 'registrations.html', context)


def register(request,sid):
    sub = Subject.objects.get(id=sid)
    user = request.user
    # Tự động tạo Mapping nếu chưa có
    mapping, created = Mapping.objects.get_or_create(
        user=user,
        defaults={'uid': user.id}
    )
    mapping.sub.add(sub)
    return redirect('/')


def unregister(request,sid):
    sub = Subject.objects.get(id=sid)
    user = request.user
    # Tự động tạo Mapping nếu chưa có
    mapping, created = Mapping.objects.get_or_create(
        user=user,
        defaults={'uid': user.id}
    )
    mapping.sub.remove(sub)
    return redirect('/')


def signin(request):
	if request.method=="POST":
		username=request.POST.get('user')
		password=request.POST.get('password')
		user=authenticate(username=username,password=password)
		if user is not None:
			login(request,user)
			return redirect('/')
		else:
			messages.error(request,"Wrong credentials,Please try again !")
			return redirect('/login/')

	if request.method == 'GET':
		return render(request, "login.html")


def signout(request):
	logout(request)
	messages.success(request,'Successfully logged out')
	return redirect('/login/')
