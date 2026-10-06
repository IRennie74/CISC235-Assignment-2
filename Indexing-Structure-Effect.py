# CISC235 Assignment 2
# Compares linear search (A) vs sort once + binary search (B)
# and finds roughly how many searches k it takes for B to win.

import random
import time

TRIALS = 5          # runs to average for each timing
MAX_VAL = 1000000   # random numbers go from 0 to this


# --- Algorithm A ---

def linear_search(nums, x):
    # just walk through the list one by one
    for i in range(len(nums)):
        if nums[i] == x:
            return "Yes"   # found it, stop early
    return "No"            # went through everything, not there


def algo_a(nums, targets):
    # one linear search per target, no setup needed
    return [linear_search(nums, t) for t in targets]


# --- Algorithm B ---

def merge_sort(arr):
    if len(arr) <= 1:
        return arr[:]          # 0 or 1 items is already sorted
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])    # sort the left half
    right = merge_sort(arr[mid:])   # sort the right half

    # merge the two halves back together
    out = []
    i = j = 0
    while i < len(left) and j < len(right):
        # take whichever front item is smaller
        if left[i] <= right[j]:
            out.append(left[i])
            i += 1
        else:
            out.append(right[j])
            j += 1
    out += left[i:]   # whatever's left over
    out += right[j:]
    return out


def binary_search(nums, x):
    lo, hi = 0, len(nums) - 1   # search range is the whole list at first
    while lo <= hi:
        mid = (lo + hi) // 2    # check the middle
        if nums[mid] == x:
            return "Yes"
        if nums[mid] < x:
            lo = mid + 1        # x must be in the right half
        else:
            hi = mid - 1        # x must be in the left half
    return "No"                 # range got empty, so x isn't there


def algo_b(nums, targets):
    srt = merge_sort(nums)   # sort once, counts toward B's time
    # then each search is just a quick binary search
    return [binary_search(srt, t) for t in targets]


# --- experiment stuff ---

def get_targets(nums, k):
    # half the targets are in the list, half definitely aren't
    lookup = set(nums)  # just for picking targets, not timed
    targets = [random.choice(nums) for _ in range(k // 2)]   # the "in" half
    while len(targets) < k:
        x = random.randint(0, MAX_VAL)
        if x not in lookup:   # only keep numbers that aren't in the list
            targets.append(x)
    random.shuffle(targets)   # mix them up so hits and misses are spread out
    return targets


def run_timed(func, nums, targets):
    # time how long one call takes
    start = time.perf_counter()
    func(nums, targets)
    return time.perf_counter() - start


def avg_times(nums, k):
    # average A and B over a few trials, same targets for both each time
    ta = tb = 0
    for _ in range(TRIALS):
        targets = get_targets(nums, k)   # new targets every trial
        ta += run_timed(algo_a, nums, targets)
        tb += run_timed(algo_b, nums, targets)
    return ta / TRIALS, tb / TRIALS


def find_k_star(nums):
    # keep doubling k until B wins, then narrow it down
    results = []   # every (k, timeA, timeB) we try, for printing later
    k = 1
    while True:
        a, b = avg_times(nums, k)
        results.append((k, a, b))
        if b < a:      # B finally won
            break
        k *= 2

    lo, hi = k // 2 + 1, k   # B lost at k/2 and won at k
    # binary search on k to find the first one where B wins
    while lo < hi:
        mid = (lo + hi) // 2
        a, b = avg_times(nums, mid)
        results.append((mid, a, b))
        if b < a:
            hi = mid       # B wins here, so k* is mid or smaller
        else:
            lo = mid + 1   # A still wins, so k* is bigger
    return lo, sorted(results)


def main():
    # quick sanity check that both algorithms agree
    test = [random.randint(0, MAX_VAL) for _ in range(500)]
    t = get_targets(test, 200)
    assert algo_a(test, t) == algo_b(test, t)
    assert merge_sort(test) == sorted(test)   # make sure my sort actually works
    print("Sanity check ok\n")

    summary = []
    for n in [1000, 2000, 5000, 10000]:
        nums = [random.randint(0, MAX_VAL) for _ in range(n)]   # duplicates are fine
        k_star, results = find_k_star(nums)

        # print every k we tried so you can see where it flips
        print(f"n = {n}")
        print(f"  {'k':>6} {'A (ms)':>10} {'B (ms)':>10}  winner")
        for k, a, b in results:
            print(f"  {k:>6} {a*1000:>10.3f} {b*1000:>10.3f}  {'B' if b < a else 'A'}")
        print(f"  k* = {k_star}, k*/n = {k_star/n:.5f}\n")
        summary.append((n, k_star))

    # final table with k* and the ratio for each n
    print("Summary")
    print(f"  {'n':>6} {'k*':>6} {'k*/n':>10}")
    for n, k_star in summary:
        print(f"  {n:>6} {k_star:>6} {k_star/n:>10.5f}")


main()
