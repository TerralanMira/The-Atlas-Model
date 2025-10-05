def guard(bio, ai):
    # if HRV drops & HR rises → damp coupling gains
    # if PLV < min_plv → widen dissent window (reduce latent_bias_gain)
    return safe_params
