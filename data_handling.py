import blackboxprotobuf


# Translating poll data into a map.
def translate_data(byte_data):
    # Decoding the data.
    message, typedef = blackboxprotobuf.decode_message(byte_data)
    # message['8'] is the actual poll.
    # message['8']['2'] is the header/question of the poll.
    header = message['8']['2'].decode('utf8')
    options = []
    # message['8']['3'] is the options of the poll, it's in a list format.
    for _message in message['8']['3']:
        # for each _message in message, _message['1'] is the option.
        options.append(_message['1'].decode('utf8'))
    votes_for = [0] * len(options)
    # message['8']['5'] is the votes per person, it's in a list format.
    for _message in message['8']['5']:
        try:
            # The actual votes can be either in a list (multiple votes) or in an int format (single vote).
            if isinstance(_message['1'], list):
                # _message['1'] is the votes.
                for _vote in _message['1']:
                    votes_for[_vote] += 1
            else:
                # _message['1'] is the vote.
                votes_for[_message['1']] += 1
        except:
            # If a person removed all his votes from the poll he will still appear but will have no votes.
            pass
    try:
        # message['8']['6'] is my vote, it is always in a map format (there is only one me).
        if isinstance(message['8']['6']['1'], list):
            for _vote in message['8']['6']['1']:
                votes_for[_vote] += 1
        else:
            votes_for[message['8']['6']['1']] += 1
    except:
        pass
    # Creating the result.
    result = {"header": header, "options": options, "votes": votes_for}
    return result
