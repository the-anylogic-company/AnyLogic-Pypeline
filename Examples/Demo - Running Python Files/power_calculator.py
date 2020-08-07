import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("base", type=float,
                        help="use the given number as the base")
    parser.add_argument("-e", "--exponent", type=float, default=2,
                        help="use the given number as the exponent (default 2)")
    parser.add_argument("-v", "--verbosity", action="count",
                        help="increase output verbosity (repeat for more; limit 2)")
    args = parser.parse_args()

    
    answer = args.base ** args.exponent
    
    if args.verbosity is None: # omitting just produces answer
        print(answer)
        
    elif args.verbosity == 1: # shows formula
        print("{}^{} == {}".format(args.base, args.exponent, answer))
        
    elif args.verbosity == 2: # explains how the square is derived
        print("multiplying {} by itself {} times is equal to {}".format(args.base, args.exponent, answer))

    else: # can't get more verbose, so complain
        raise Exception("That's too verbose!")
