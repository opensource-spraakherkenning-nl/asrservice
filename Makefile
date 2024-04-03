.PHONY: docker docker-cpu docker-gpu 

docker: docker-cpu docker-gpu

docker-cpu:
	docker build -t proycon/asrservice .

docker-gpu:
	docker build -t proycon/asrservice:gpu --file gpu.Dockerfile
