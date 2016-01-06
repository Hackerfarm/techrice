
def token_required(endpoint):
	def token_check(token):
		if token == 1:
			return endpoint(token)
		else:
			return 'invalid token'
	return token_check
			
@token_required
def index(token):
	return 'token was {}'.format(token)

if __name__ == '__main__':
	print index(1)

# endpoint = token_required(endpoint)
