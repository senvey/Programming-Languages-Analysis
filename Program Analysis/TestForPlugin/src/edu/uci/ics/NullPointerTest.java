package edu.uci.ics;

public class NullPointerTest {

	private int x;
	
	public void issueNPE() throws Exception {
		String nullPointer = null;
		// MethodInvocation
//		nullPointer.charAt(0);
		
		int[] nullArray = null;
		// ArrayAccess
		System.out.println(nullArray[0]);
		// QulifiedName
		System.out.println(nullArray.length);
		nullArray.length = 1;
		
		int a = this.x;
		int b = 2;
		int c = 3;
		int d = 4;
		int m = 5;
		int n = 6;
		// InfixExpression
		int i = (a + b) + c + d;
		// Initializer in Declaration
		int j = m;
		// SimpleName in Assignment
		j = n;
		// InfixExpression
		j = a + b + c + 1;
		
		// MethodInvocation
		System.out.println(i);
		
		String s = "test";
		// MethodInvocation
		s.replace('t', 'h');
		
		if (s != "")
			System.out.println();
	}
	
	public void foo() {
		issueNPE();
		try {
			issueNPE();
		} catch (Exception e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}
}
