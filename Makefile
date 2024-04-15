.PHONY: docker docker-cpu docker-gpu 

docker: docker-cpu docker-gpu

docker-gpu:
	docker build -t proycon/asrservice .

docker-cpu:
	docker build -t proycon/asrservice:cpu --file cpu.Dockerfile
