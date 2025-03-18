import matplotlib.pyplot as plot
import numpy as np
import math
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

def orderplanets(lst,element):
    try:element_list = [float(x[element]) for x in lst]
    except:return False
    ordered_list = sorted(element_list)
    return ordered_list

#___ Initialising Firebase ___#
cred = credentials.Certificate("exoplanet-dataset-firebase-adminsdk-shser-16bd9bf498.json")
firebase_admin.initialize_app(cred, {'databaseURL':'https://exoplanet-dataset-default-rtdb.europe-west1.firebasedatabase.app/'})
ref = db.reference('/')
firebase_content = ref.get('/users/Planet Info', None)

#___ Making Lists and Dictionaries ___#
planetdict = firebase_content[0]["Planet Info"]
earthlike = {"Planets":{},"Averages":{}}
superearth = {"Planets":{},"Averages":{}}
megaearth = {"Planets":{},"Averages":{}}
neptunelike = {"Planets":{},"Averages":{}}
jupiterlike = {"Planets":{},"Averages":{}}
hotjupiter = {"Planets":{},"Averages":{}}
browndwarf = {"Planets":{},"Averages":{}}
outlier_planets = {"Planets":{},"Averages":{}}
planet_categories = {"Earthlike":earthlike,"Super Earth":superearth,"Mega Earth":megaearth,"Neptunelike":neptunelike,"Jupiterlike":jupiterlike,"Hot Jupiter":hotjupiter,"Brown Dwarf":browndwarf}
numerical_type = ["sy_snum","sy_pnum","pl_orbsmax","pl_orbper","pl_rade","pl_radj","pl_bmasse","pl_bmassj","pl_dens","pl_orbeccen","pl_insol","pl_eqt","pl_orbincl","ttv_flag","pl_imppar","pl_orblper","st_teff","st_mass","st_lum","st_logg","ra","dec","sy_dist","sy_vmag","sy_kmag","sy_gaiamag","sy_gaiamagerr1","sy_gaiamagerr2"]
list_of_radii = []
all_radii = []
all_masses = []
telescopecounts = {}


#___ Organising Data ___#       
for planet,data in planetdict.items():
    sy_pnum = int(data["sy_pnum"])
    E_mass = data["pl_bmasse"]
    E_radius = data["pl_rade"]
    if E_mass < 17 and E_radius < 8 and len(all_masses) < 400:
        all_masses.append(E_mass)
        all_radii.append(E_radius)
    if data.get("pl_orbper"): orbital_period = data["pl_orbper"]
    else: orbital_period = False
    if E_mass < 2 and E_radius < 2.5: earthlike["Planets"][planet] = data
    elif E_mass < 10 and E_radius < 4: superearth["Planets"][planet] = data
    elif E_mass < 17 and E_radius < 8:megaearth["Planets"][planet] = data
    else:
        if orbital_period:
            if orbital_period < 10: hotjupiter["Planets"][planet] = data
        if not hotjupiter["Planets"].get(planet):
            if E_mass < 125: neptunelike["Planets"][planet] = data
            elif E_mass > 125 and data["pl_bmassj"] < 75:jupiterlike["Planets"][planet] = data
            else: browndwarf["Planets"][planet] = data
                    
#___ Tallying up Telescope Discoveries ___#
    telescope = data["disc_telescope"]
    if telescopecounts.get(telescope): telescopecounts[telescope] = telescopecounts[telescope] + 1
    else: telescopecounts[telescope] = 1

#___ Analysing and Finding Averages ___#
for i,category in enumerate(planet_categories):
    planets = planet_categories[category]["Planets"]
    averages = planet_categories[category]["Averages"]
    for planet,data in planets.items():
        for element,value in data.items():
            if element in numerical_type:
                if value:
                    if averages.get(element):
                        averages[element] = (value+averages[element][0],averages[element][1]+1)
                    else:
                        averages[element] = (value,1)
    
    #______ Printing Averages ______#
    print(f"\n\n{category} Planets:")
    for element in averages:
        total = averages[element][0]
        values = averages[element][1]
        averages[element] = total/values
        if element == "sy_pnum": total_pnum = values
        if element == "pl_rade": list_of_radii.append(total/values)
        print(f"-----average {element} is {averages[element]}")
    print(f"Data gathered from {total_pnum} planets.")


#______ Graphs and Charts ______#

Analytics = {"Graph_Info":{},"Averages":{"Earthlike":earthlike["Averages"],"Super Earth":superearth["Averages"],"Mega Earth":megaearth["Averages"],"Neptunelike":neptunelike["Averages"],"Jupiterlike":jupiterlike["Averages"],"Hot Jupiter":hotjupiter["Averages"],"Brown Dwarf":browndwarf["Averages"]}} #Creating Analytics Dict

#__ Scatter Plot of Radius to Mass __#
plot.scatter(all_masses,all_radii)
plot.title('Terrestrial Exoplanet Radius to Mass Ratio')
plot.xlabel('Planet Mass (Earth masses)')
plot.ylabel('Planet Radius (Earth Radii)')
Analytics["Graph_Info"]["Radius to Mass Ratio"] = {}
massradii_dict = {}
massradii_sorted_dict = {}
for index,Mass in enumerate(all_masses): massradii_dict[Mass] = all_radii[index]
for Sorted_Mass in sorted(all_masses):
    massradii_sorted_dict[Sorted_Mass] = massradii_dict[Sorted_Mass]
Analytics["Graph_Info"]["Radius to Mass Ratio"]["Masses"] = list(massradii_sorted_dict.keys())
Analytics["Graph_Info"]["Radius to Mass Ratio"]["Radii"] = list(massradii_sorted_dict.values())
plot.show()

#___ Pie Chart of Habitable Planets and Total Planets___#
cats = ["Earthlikes","Super Earths","Mega Earths","Neptunelikes","Jupiterlikes","Hot Jupiters","Brown Dwarfs"]
counts = [len(earthlike["Planets"]),len(superearth["Planets"]),len(megaearth["Planets"]),len(neptunelike["Planets"]),len(jupiterlike["Planets"]),len(hotjupiter["Planets"]),len(browndwarf["Planets"])]
fig, ax = plot.subplots()
ax.pie(counts, labels=cats, autopct='%1.1f%%',colors=['green', 'yellow', 'grey',"blue","orange","red","brown"])
plot.title('Most Common Types of Exoplanet')
Analytics["Graph_Info"]["All Planets"] = {}
Analytics["Graph_Info"]["All Planets"]["Categories"] = cats
Analytics["Graph_Info"]["All Planets"]["Counts"] = counts
plot.show()


#___ Pie Chart of Telescopes Used___#
tels = []
counts = []
othercount = 0
for telescope,count in telescopecounts.items():
    if count > 50:  
        tels.append(telescope)
        counts.append(count)
    else:
        othercount += 1
tels.append("Other Telescopes")
counts.append(othercount)
fig, ax = plot.subplots()
ax.pie(counts, labels=tels, autopct='%1.1f%%')
plot.title('Most Common Telescopes Used to Discover Exoplanets (In Database)')
plot.show()
Analytics["Graph_Info"]["Telescopes"] = {}
Analytics["Graph_Info"]["Telescopes"]["Names"] = tels
Analytics["Graph_Info"]["Telescopes"]["Counts"] = counts


#__ Radius Chart of Average Radius per Category __#
plot.title('Average Earth Radii per Planet Type')
plot.xlabel('Planet Types: Earthlikes,Super Earths,Mega Earths,Neptunelikes,Jupiterlikes,Hot Jupiters,Brown Dwarfs')
plot.ylabel('Radius Length: Average Earth Radii')
theta = np.linspace(0.0, 2 * np.pi, 7, endpoint=False)
width = (2*np.pi)/7
ax = plot.subplot(projection='polar')
ax.bar(theta, list_of_radii, width=width, bottom=0.0, color=['green', 'yellow', 'grey',"blue","orange","red","brown"], alpha=0.5)
plot.show()
Analytics["Graph_Info"]["Radii"] = list_of_radii


#___ Transferring Data to FireBase ___#
ref = db.reference('/Analytics')
ref.set(Analytics)