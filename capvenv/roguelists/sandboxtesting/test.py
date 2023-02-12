blacklistlower = ['bundle', 'demo', 'soundtrack', 'dlc', 'sound track', ' pack', 'double xp', 'triple xp', 'double money', 'triple money', 'audiobook', 'coming soon', 'to be announced', 'free demo', 'free trial', 'game assets', '- skin', 'bonus content']
temp = ' '.join(blacklistlower)

a = "No Turning Back: Potions Starter Pack"

for word in blacklistlower:
  if word in a.lower():
    b = True

print(a.lower())
print(temp)
print(b)