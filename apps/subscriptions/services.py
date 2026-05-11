# apps/subscriptions/services.py

def get_user_plan(user):
    """
    Retorna o plano do utilizador.
    Por enquanto, todos os utilizadores são 'free'.
    """
    # Se já tiveres um campo 'plan' no modelo User, podes usá-lo
    if hasattr(user, 'plan') and user.plan:
        return user.plan
    return 'free'