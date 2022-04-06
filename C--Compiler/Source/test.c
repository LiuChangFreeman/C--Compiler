function int max(int a, int b)
{
    if (a > b)
        return a;
    else
        return b;
}
function int min(int A, int B)
{
    if (A < B)
        return A;
    else
        return B;
}
function int re(int n)
{
    if (n < 1)
        return 1;
    else
    {
        int a = function re(n - 1);
        int b = n * a;
        return b;
    }
}
function int main()
{
    int p, q;
    p = function re(5);
    int a = 1, b = 234, c = 2, d = 3 * 4 + 5 - 6;
    int sum = 1;
    for (int i = 1; i < 100; i += 1)
    {
        if (i < 50)
            continue;
        else
            sum += i;
        if (i > 98)
            break;
        else
            p = 1 + 1, b = 5 * 4, c += d;
    }
    int t = function min(c, d);
    int k = 1 * 2 + 3 / (4 * 8) - 6 + a - b + t;
    while (k < 40)
    {
        k += a;
    }
    int s = ((534 - 23) + 423) * 23 + k;
    return s;
}