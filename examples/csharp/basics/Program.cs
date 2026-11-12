using System;
using System.Collections.Generic;

int minimum = 3;
if (args.Length > 1 || (args.Length == 1 && !int.TryParse(args[0], out minimum)))
{
    Console.Error.WriteLine("Expected one integer threshold or no arguments.");
    return 2;
}

List<int> scores = new() { 2, 5 };
scores.Add(3);
Console.WriteLine($"Count: {CountAtLeast(scores, minimum)}");
return 0;

static int CountAtLeast(List<int> scores, int minimum)
{
    int count = 0;
    foreach (int score in scores)
    {
        if (score >= minimum)
        {
            ++count;
        }
    }
    return count;
}
