try:
    import torch

    print(torch.cuda.is_available())

    if torch.cuda.is_available():
        print(torch.cuda.get_device_name(0))

except Exception as e:
    print(e)