# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - api is an example of Hypermedia API support and access control
#########################################################################
import datetime
auth.settings.register_next = URL('default','pick')
z=0
f=0
db.For_Borrow.truncate()
db.For_Purchase_Requests.truncate()
db.Search_Book.truncate()
for row in db(db.Book_Requests.id >0).select():
    for row1 in db(db.Book_Requests.id >0).select():
        if row1.id==row.id:
            continue
        if row1.Book_Id==row.Book_Id and row1.User_Id==row.User_Id:
            f=1
            del db.Book_Requests[row.id]
    if f==1:
        break
#handles multiple borrow
f=0
for row2 in db(db.Borrow.id >0).select():
    for row3 in db(db.Borrow.id > 0).select():
        if row3.id ==row2.id:
            continue
        if row2.Book_Id==row3.Book_Id and row2.User_Id==row3.User_Id:
            f=1
            del db.Borrow[row3.id]
    if f==1:
        break
#delete requested if borrow
for row in db(db.Book_Requests.id >0).select():
    for row1 in db(db.Borrow.id >0).select():
        if row1.Book_Id==row.Book_Id and row1.User_Id==row.User_Id:
            del db.Book_Requests[row.id]

#pick group if not assigned

def role():
    type=request.args[0]
    if not db(db.auth_group.role==type).count():
         db.auth_group.insert(role=type)
    auth.add_membership(type)
    redirect(URL('index'))

def pick():
    form=SQLFORM(db.Members)
    if form.accepts(request,session):
        response.flash='Form accepted'
        redirect(URL('role',args=[form.vars.Type_of_Account]))
    elif form.errors:
        response.flash='Form contains errors'
    return dict(form=form)

def index():
    if auth.has_membership(group_id='Librarian'):
        redirect(URL('default', 'indexl'))
    b=0
    d=0
    au=0
    one=0
    two=0
    an=0
    if auth.user_id > 0:
        au=auth.user_id
        an=auth.user.first_name
    form=SQLFORM(db.Search_Book)
    if form.accepts(request,session):
        one=1
        response.flash='Form accepted'
        redirect(URL('get',args=[form.vars.Category,form.vars.Search_Word]))

    form1= FORM(INPUT(_name='request'),INPUT(_value='Reserve',_type='submit'))
    if form1.accepts(request,session):
        response.flash='Form accepted'
        a=str(form1.vars)
        a=a.split(": '")
        a= a[1][:-3]
        if len(a)>0:
            two=1
            a=int(a)
            b=auth.user_id
            d=1
            redirect(URL('reserves',args=[a,b]))
        else:
           two=2
    form2= FORM(INPUT(_value='View',_type='submit'))
    if form2.accepts(request,session):
        pass
    elif form2.errors:
        pass
    else:
        if one==0 and two==2:
            redirect(URL('views',args=[au,an]))
    return dict(au=au,an=an,b=b,d=d,form=form,form1=form1,form2=form2,z=z)

def get():
    search=request.args[0]
    keywords = request.args[1].split('_')

    if(search=="Author" or search=="All"):
        query1 = reduce(lambda a,b:a|b,[db.Catalogue.Author.like('%'+key+'%') for key in keywords])
    if(search=="Title" or search=="All"):
        query2 = reduce(lambda a,b:a|b,[db.Catalogue.Title.like('%'+key+'%') for key in keywords])
    if(search=="Year" or search=="All"):
        query3 = reduce(lambda a,b:a|b,[db.Catalogue.Year_of_Publication.like('%'+key+'%') for key in keywords])
    if(search=="Genre" or search=="All"):
        query4 = reduce(lambda a,b:a|b,[db.Catalogue.Categories.like('%'+key+'%') for key in keywords])
    if(search=="All"):
        books = db(query1|query2|query3|query4).select(orderby=db.Catalogue.id)
    if(search=="Author"):
        books = db(query1).select(orderby=db.Catalogue.Author)
    if(search=="Title"):
        books = db(query2).select(orderby=db.Catalogue.Title)
    if(search=="Year"):
        books = db(query3).select(orderby=db.Catalogue.Year_of_Publication)
    if(search=="Genre"):
        books = db(query4).select(orderby=db.Catalogue.Categories)
    books=str(books).split(',')
    books=books[8:]
    for i in range(0,len(books)):
        if i%8==0:
            books[i]=books[i][-2:]
    del books[len(books)-1]
    return dict(books=books)

def requests():
    form=SQLFORM(db.Purchase_Requests)
    if form.accepts(request,session):
        response.flash='Form accepted'
    elif form.errors:
        response.flash='Form contains errors'
    return dict(form=form)

def reserves():
    flag=0
    z=0
    b=request.args[1]
    if len(b) > 0 and b!='None':
        b=int(b)
    for row in db(db.Catalogue.id >0).select():
        if row.id==int(request.args(0)):
                flag=1
                if auth.has_membership(group_id='Student') and row.Reference_Book==True and b>0:
                        z=1
                else:
                    db.Book_Requests.insert(Book_Id=request.args(0),User_Id=auth.user_id)
    return dict(b=b,flag=flag,z=z)
def logout():
    if auth.user_id>0:
        auth.logout()
    else:
        redirect(URL('user'))
def views():
    ids=int(request.args[0])
    book=0
    form=FORM('Book Id: ',INPUT(_name='Book_Id'),INPUT(_value='Cancel',_type='submit'))
    if form.accepts(request,session):
        book=int(form.vars.Book_Id)
        for row in db(db.Book_Requests.id >0).select():
            if row.Book_Id==book:
                del db.Book_Requests[row.id]
    days={}
    for page in db(db.Borrow).select():
        if page.User_Id==ids:
            b=str(page.Borrowed_On)
            b=b[:-9]
            b=b.split('-')
            a=datetime.date.today()
            a=str(a).split('-')
            aa=datetime.datetime(int(a[0]),int(a[1]),int(a[2]),0,0,0)
            bb=datetime.datetime(int(b[0]),int(b[1]),int(b[2]),0,0,0)
            cc=aa-bb
            days[page.Book_Id]=cc.days
    form1=SQLFORM(db.Purchase_Requests)
    if form1.accepts(request,session):
        response.flash='Request will be taken into consideration'
    return dict(days=days,form=form,ids=ids,form1=form1)


@auth.requires_membership('Librarian')
def indexl():
    a=auth.user.id
    form3=FORM(INPUT(_value='Logout',_type='submit'))
    if form3.accepts(request,session):
        auth.logout()
    form=SQLFORM(db.For_Borrow)
    if form.accepts(request,session):
        if form.vars.Borrow=='Borrow' or form.vars.Borrow=='Return':
            redirect(URL('action',args=[form.vars.Borrow]))
        if form.vars.Borrow=='View borrowed' or form.vars.Borrow=='View requests':
            redirect(URL('view',args=[form.vars.Borrow]))

    form1=SQLFORM(db.Catalogue)
    if form1.accepts(request,session):
        response.flash='Form accepted'
    elif form1.errors:
        response.flash='Form contains errors'
    form2=SQLFORM(db.For_Purchase_Requests)
    if form2.accepts(request,session):
        if form2.vars.Purchase=='Approve' or form2.vars.Purchase=='Reject':
            redirect(URL('action',args=[form2.vars.Purchase]))
        if form2.vars.Purchase=='View':
            redirect(URL('view',args=[form2.vars.Purchase]))
    return dict(form=form,form1=form1,form2=form2,form3=form3)

@auth.requires_membership('Librarian')
def action():
    zz=0
    ret=0
    zzz=0
    flag=0
    flag1=0
    flag3=0
    bor=0
    if request.args(0)=='Borrow':
        form=FORM('Book Id:',INPUT(_name='Book_Id'),
                  'User Id:',INPUT(_name='User_Id'),
                   INPUT(_value='Borrow',_type='submit'))
        if form.accepts(request,session):
            bor=1
            a= form.vars.User_Id
            b=form.vars.Book_Id
            if len(a)>0 and len(b)>0:
                a=int(a)
                b=int(b)
                for row in db(db.Catalogue.id >0).select():
                    if row.id==b and row.Reference_Book==True and auth.has_membership('Student',a):
                        zz=1
                        break #zz-student trying to borrow ref,zzz-book not on shelf;
                if zz==0:
                    for row in db(db.Catalogue.id>0).select():
                        if row.id==b:
                            flag=1
                    for row1 in db(db.auth_user.id>0).select():
                        if row1.id==a:
                            flag1=1
                            for row in db(db.Catalogue.id>0).select():
                                if row.id==b:
                                    flag=1
                                    if row.On_Shelf==True:
                                        row.On_Shelf = False
                                        row.update_record()
                                        db.Borrow.insert(Book_Id=b,User_Id=a)
                                    else:
                                        zzz=1

    elif request.args(0)=='Return':
        form=FORM('Book Id:',INPUT(_name='Book_Id'),
                  'User Id:',INPUT(_name='User_Id'),
                   INPUT(_value='Return',_type='submit'))
        if form.accepts(request,session):
            ret=1
            a= form.vars.User_Id
            b=form.vars.Book_Id
            if len(a)>0 and len(b)>0:
                a=int(a)
                b=int(b)
                for row in db(db.Catalogue.id>0).select():
                    if row.id==b:
                        for row1 in db(db.Borrow.id>0).select():
                            if row1.User_Id==a:
                                flag3=1
                                row.On_Shelf = True
                                row.update_record()
                                db(db.Borrow.Book_Id==b).delete()
    elif request.args(0)=='Approve':
            form=FORM('Title:',INPUT(_name='Title'),INPUT(_value='Approve',_type='submit'))
            if form.accepts(request,session):
                for row in db(db.Purchase_Requests).select():
                        if row.Title==form.vars.Title:
                            db.Catalogue.insert(Title=row.Title,Author=row.Author,Year_of_Publication=row.Year_of_Publication,Categories=row.Categories)
                            del db.Purchase_Requests[row.id]
    else:
        form=FORM('Title',INPUT(_name='Title'),INPUT(_name='Title',_value='Reject',_type='submit'))
        if form.accepts(request,session):
            for row in db(db.Purchase_Requests.id >0).select():
                if row.Title==form.vars.Title:
                    del db.Purchase_Requests[row.id]
    a=request.args(0)
    print bor,flag3
    return dict(flag3=flag3,ret=ret,bor=bor,zzz=zzz,form=form,flag=flag,flag1=flag1,a=a,zz=zz)

@auth.requires_membership('Librarian')
def view():
    a=request.args(0)
    return dict(a=a)

def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/manage_users (requires membership in
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())


@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


@auth.requires_login()
def api():
    """
    this is example of API with access control
    WEB2PY provides Hypermedia API (Collection+JSON) Experimental
    """
    from gluon.contrib.hypermedia import Collection
    rules = {
        '<tablename>': {'GET':{},'POST':{},'PUT':{},'DELETE':{}},
        }
    return Collection(db).process(request,response,rules)
