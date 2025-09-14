class Mod:
	def __init__(self,num1,num2):
		self.num1=num1
		self.num2=num2
	def add(self):
		print(self.num1+self.num2)
	def sub(self):
		print(self.num1-self.num2)
	def mul(self):
		print(self.num1*self.num2)
	def div(self):
		print(self.num1//self.num2)

num1=int(input("계산을 수행할 첫번째 수"))
num2=int(input("계산을 수행할 두번째 수"))

mod=Mod(num1,num2)
mod.add()
mod.sub()
mod.mul()
mod.div()
