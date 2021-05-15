import eel
import desktop
import mynavi

app_name="html"
end_point="index.html"
size=(2000,1300)

@ eel.expose
def main(search_keyword):
    mynavi.main(search_keyword)
    
desktop.start(app_name,end_point,size)
# # desktop.start(size=size,appName=app_name,endPoint=end_point)