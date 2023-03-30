import random
from math import sqrt

def inverse_triangular(min_, antimode, max_, verbose=False):
    """
    A custom distribution that acts like an inverted triangular distribution,
        where the "inverse_mode" is the least likely to occur and the extreme bounds are more likely
        (and both equally so).
    The mean of the distribution can be found by doing: `(2*min_ + 2*max_ - antimode) / 3`

    NOTE: This is only intended for demo purposes and not meant to be practical or realistic.
    """
    # re-assign variables if they're not passed in the intended order
    if min_ > max_:
        min_, max_ = max_, min_
    if antimode < min_:
        min_, antimode = antimode, min_
    elif antimode > max_:
        max_, antimode = antimode, max_

    # use traditional triangular distribution generation
    # but offset from mode point rather than from boundary point
    antimode_ratio = (antimode - min_) / (max_ - min_)

    if verbose:
        print("Choosing a random number with the following properties:")
        print(f"\tRange:    [{min_}, {max_}]")
        print(f"\tAntimode: {antimode}")
        print(f"\tMean:     {(2*min_ + 2*max_ - antimode)/3:.3f}")
    
    U = random.random()
    if U < antimode_ratio:
        # choose from triangle to the left (lower) of the antimode
        return random.triangular(min_, antimode, min_)
    else:
        # choose from triangle to the right (higher) of the antimode
        return random.triangular(antimode, max_, max_)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate a random number using an inverted triangular distribution")
    parser.add_argument("min", type=float, help="The lower bound of the distribution")
    parser.add_argument("antimode", type=float, help="The mid-point of the distribution (least likely to occur)")
    parser.add_argument("max", type=float, help="The upper bound of the distribution")
    parser.add_argument("--seed", type=int, help="The number to use for the random number generator (for reproducible outputs); omitting uses a random seed.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Print debug information")
    args = parser.parse_args()

    # set the random seed and include logging messages if requested
    if args.seed:
        if args.verbose: print("Setting the random seed to", args.seed)
        random.seed(args.seed)
    elif args.verbose: print("Using a random seed")

    print(inverse_triangular(args.min, args.antimode, args.max, args.verbose))

    
    
        
