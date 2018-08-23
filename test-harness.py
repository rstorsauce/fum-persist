from fum import fum_yield

index = 0

if __name__ == '__main__':
	while True:
		fum_yield()
		print("run triggered")
		print(index)
		index += 1
