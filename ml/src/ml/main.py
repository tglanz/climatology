from neuralop.models import FNO

if __name__ == '__main__':
    print("creating operator")
    operator = FNO(n_modes=(64, 64),
               hidden_channels=64,
               in_channels=2,
               out_channels=1)
    print("created operator")

    