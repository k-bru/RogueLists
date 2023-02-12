from datetime import datetime

#"Jul 8, 2023"
#Length is ALWAYS 11 OR 12
#[5] OR [6] is ALWAYS a comma
#[-4:-2] is ALWAYS 20

#If RELEASE.length == 11 OR 12 
# AND [-4:-2] == 20 
# AND [5] OR [6] == ","
s = "Jul 8, 2023"
d = datetime.strptime(s, '%b %d, %Y')
normalDateFinal = d.strftime('%Y-%m-%d')


#"November 2021"
#Length varies
#[5] AND [6] are NEVER a comma
#[-4:-2] is ALWAYS 20

#If RELEASE[5] OR [6] != "," 
#AND [-4:-2] == 20
a = "November 2021"
b = datetime.strptime(a, '%B %Y')
writtenDateFinal = b.strftime('%Y-%m-%d')


#"Q2 2026"
#Length is ALWAYS 7
#[0] is ALWAYS Q

#If RELEASE.length == 7 
#AND [0] == 'Q'
q = "Q2 2026"
qConvertMonth = (int(q[1]) * 3)
qConvertYear = q[-4:]
q2 = f"{qConvertMonth} {qConvertYear}"
w = datetime.strptime(q2, '%m %Y')
quarterDateFinal = w.strftime('%Y-%m-%d')


#"2023"
#Length is ALWAYS 4
#[0:2] is ALWAYS 20

#If RELEASE.length == 4 
# AND [0:2] == 20
y = "2023"
y2 = f"{y}-12-31"


print("Normal Date:")
print(f"Original: {s} \nConverted: {normalDateFinal}\n")
print("Written Date No Day:")
print(f"Original: {a}\nConverted: {writtenDateFinal}\n")
print("Quarter Date:")
print(f"Original: {q}\nConverted: {quarterDateFinal}\n")
print("Only Year:")
print(f"Original: {y}\nConverted: {y2}")
