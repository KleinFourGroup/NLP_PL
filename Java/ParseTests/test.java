class Tester {
	static String v = "0.0.13";

	public void t1(int a, int b) {
		a *= b;
	}

	public char t2() {
		return 'b';
	}

	public static void main(String[] args) {
		char c = v[0];
		float x;
		int n, m;
		n = 2;
		m = 3;
		x = 0f;
		t1(m, n);
		v = t2();

		{
			boolean b = false;
			x = 5f;
		}

		int j = 0;
		while (j < 5) {
			t1(m, n);
			j++;
		}
		
		do {
			t1(m, n);
			j++;
		} while (j < 5);

		//HELLO

		for(int i = 0, k=i; i < 6 && k < 7; i++, j++) {
			c = v[i];
		}

		if (c == 'a') t1(11, 12);

		if (c == 'a') t1(11, 12);
		else v = t2();

		switch(n) {
			case 0:
				t1(5,m);
				t1(n,7);
			case 2:
				t1(5,m);
				t1(n,7);
				break;
			case 2:
				t1(5,m);
				t1(n,7);
			default:
				t1(5,m);
				t1(n,7);
		}
	}
}
