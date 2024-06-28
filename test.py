
def predict(text):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    args = argparse.Namespace(
        vocab_path='vocab.json',
        hidden_size=256,
        dropout_rate=0.2,
        device=device
    )
    vocab = build_vocab(args)
    label_map = vocab.labels
    model = RNN_ATTs(len(vocab.vocab), 300, 256,
                     len(label_map), n_layers=1, bidirectional=True, dropout=args.dropout_rate)
    model.load_state_dict(torch.load('model.th'))
    model.to(device)
    model.eval()

    with torch.no_grad():
        # 对输入的文本进行分词
        text = jieba.lcut(text)
        # 将文本转化为模型可以接受的形式
        input_tensor = vocab.vocab.to_input_tensor([text], args.device)
        # 使用模型进行预测
        logits = model(input_tensor)
        # 选取预测结果中概率最大的类别
        preds = torch.argmax(logits, dim=1)
        # 将预测结果从tensor转化为numpy数组
        preds = preds.detach().cpu().numpy()

    return preds[0]  # 如果只有一个句子，返回预测结果的第一个元素