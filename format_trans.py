def wav_to_pcm(input_dir, out_dir) :
    with open(input_dir, 'rb') as wavfile:
        ori_data = wavfile.read() ## 读出来是裸流bytes数据
        wavfile.close()
    with open(out_dir, 'wb') as pcmfile:
        pcmfile.write(ori_data)
        pcmfile.close()
        print('成功转pcm')

if __name__ == '__main__':
    wav_to_pcm('output.wav', 'output.pcm')